// Melody <-> binary pitch x time grid (Demo C). Pure functions, no DOM.
// The Python version in 01_binary_grid.ipynb follows the same rules.
//
// A cell covers [i / res, (i + 1) / res) quarter notes. Two sets of rules:
// "demo": a note fills every cell whose start lies inside the note (what sounds
//   at the start of the cell); notes that cover no cell start are lost. The grid
//   is read back column by column, as a sequence of chords.
// "camat": as CAMAT's create_binary_matrix, onsets are floored and ends ceiled,
//   so a note fills every cell it touches. The grid is read back row by row, as
//   CAMAT's binary_slice_to_df does: each run of 1s is one note. CAMAT has no
//   onset layer (yet), so this read-back ignores onsets.

const NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

export function pitchName(midi) {
  return NAMES[midi % 12] + (Math.floor(midi / 12) - 1);
}

export function isBlackKey(midi) {
  return NAMES[midi % 12].length > 1;
}

// Notes from a Verovio timemap: [{pitch, on, off}] in quarter notes.
// pitches: Map xml:id -> MIDI pitch (pitchesFromMEI in mei.js); ids not in
// the map (rests) are skipped.
export function notesFromTimemap(timemap, pitches) {
  const offs = new Map();
  for (const event of timemap) for (const id of event.off || []) offs.set(id, event.qstamp);
  const notes = [];
  for (const event of timemap) {
    for (const id of event.on || []) {
      if (!pitches.has(id)) continue;
      notes.push({ pitch: pitches.get(id), on: event.qstamp, off: offs.get(id) ?? event.qstamp });
    }
  }
  return notes.sort((a, b) => a.on - b.on || a.pitch - b.pitch);
}

export function barQuarters(meter) {
  return (meter.count * 4) / meter.unit;
}

// Start of the cell grid: round to avoid 0.9999 artefacts.
const EPS = 1e-9;

export function toGrid(notes, { res, meter, rule = "demo" }) {
  const barCells = Math.round(barQuarters(meter) * res);
  const end = Math.max(0, ...notes.map((n) => n.off));
  const bars = Math.max(1, Math.ceil(end / barQuarters(meter) - EPS));
  const nCols = bars * barCells;
  const pitches = notes.map((n) => n.pitch);
  const low = Math.min(...pitches);
  const high = Math.max(...pitches);
  const occ = {};
  const ons = {};
  for (let p = low; p <= high; p++) {
    occ[p] = new Uint8Array(nCols);
    ons[p] = new Uint8Array(nCols);
  }
  const lost = [];
  const moved = []; // kept, but starting or ending at a different time
  for (const n of notes) {
    const first = rule === "camat" ? Math.floor(n.on * res + EPS) : Math.ceil(n.on * res - EPS);
    const stop = Math.ceil(n.off * res - EPS); // first cell not covered
    if (first >= stop || n.off - n.on < EPS) {
      lost.push(n);
      continue;
    }
    if (Math.abs(first - n.on * res) > EPS || Math.abs(stop - n.off * res) > EPS) moved.push(n);
    for (let i = first; i < stop && i < nCols; i++) occ[n.pitch][i] = 1;
    ons[n.pitch][first] = 1;
  }
  return { res, meter, rule, barCells, nCols, low, high, occ, ons, lost, moved };
}

// Rows to show, highest first. compact: hide black-key rows that stay empty.
export function gridRows(grid, compact = true) {
  const rows = [];
  for (let p = grid.high; p >= grid.low; p--) {
    if (compact && isBlackKey(p) && !grid.occ[p].some((v) => v)) continue;
    rows.push(p);
  }
  return rows;
}

// Grid as text, one row per pitch, cells grouped by bar (as on the slides).
export function gridToText(grid, { compact = true, onsets = false } = {}) {
  const rows = gridRows(grid, compact);
  const bars = grid.nCols / grid.barCells;
  const width = Math.max(grid.barCells, 5) + 2;
  const label = (s) => s.padEnd(6);
  const block = (cells) => {
    const lines = [label("") + Array.from({ length: bars }, (_, b) => `bar ${b + 1}`.padEnd(width)).join("").trimEnd()];
    for (const p of rows) {
      let line = label(pitchName(p));
      for (let b = 0; b < bars; b++) {
        line += Array.from(cells[p].slice(b * grid.barCells, (b + 1) * grid.barCells)).join("").padEnd(width);
      }
      lines.push(line.trimEnd());
    }
    return lines.join("\n");
  };
  if (!onsets) return block(grid.occ);
  // Both grids in one: a note can only start where a pitch sounds, so three values are enough.
  const three = {};
  for (const p of rows) three[p] = Array.from(grid.occ[p], (v, i) => (v ? (grid.ons[p][i] ? 2 : 1) : 0));
  return `Sounding (1 = the pitch sounds):\n${block(grid.occ)}\n\nOnsets (1 = a note starts):\n${block(grid.ons)}`
    + `\n\nBoth in one grid (2 = a note starts, 1 = it continues, 0 = silence):\n${block(three)}`;
}

// Read the grid back as events: a new event starts whenever the set of
// sounding pitches changes or (with onsets) a sounding pitch has an onset.
export function gridToEvents(grid, { onsets = false } = {}) {
  const events = [];
  let current = null;
  for (let i = 0; i < grid.nCols; i++) {
    const active = [];
    let attack = false;
    for (let p = grid.low; p <= grid.high; p++) {
      if (grid.occ[p][i]) {
        active.push(p);
        if (onsets && grid.ons[p][i]) attack = true;
      }
    }
    const key = active.join(",");
    if (current && current.key === key && !attack) {
      current.len += 1;
    } else {
      current = { key, start: i, len: 1, pitches: active };
      events.push(current);
    }
  }
  return events.map(({ start, len, pitches }) => ({ start, len, pitches }));
}

// Read the grid back with its rules: { events (for eventsToKern), notes, cut }.
// cut: how often the column-by-column reading cuts a held note because
// another pitch starts or stops while it sounds.
export function readGrid(grid, { onsets = false } = {}) {
  if (grid.rule === "camat") {
    const notes = gridToNotes(grid);
    return { events: notesToEvents(notes, grid), notes, cut: 0 };
  }
  const events = gridToEvents(grid, { onsets });
  let cut = 0;
  for (let k = 1; k < events.length; k++) {
    const i = events[k].start;
    for (const p of events[k].pitches) {
      if (events[k - 1].pitches.includes(p) && !(onsets && grid.ons[p][i])) cut += 1;
    }
  }
  return { events, notes: eventsToNotes(events, grid.res), cut };
}

// Row by row, as CAMAT reads its grids: each run of 1s in one row is one note,
// so repeated notes of the same pitch merge.
export function gridToNotes(grid) {
  const notes = [];
  for (let p = grid.low; p <= grid.high; p++) {
    let start = -1;
    for (let i = 0; i <= grid.nCols; i++) {
      const on = i < grid.nCols && grid.occ[p][i] === 1;
      if (start >= 0 && !on) {
        notes.push({ pitch: p, on: start / grid.res, off: i / grid.res });
        start = -1;
      }
      if (on && start < 0) start = i;
    }
  }
  return notes.sort((a, b) => a.on - b.on || a.pitch - b.pitch);
}

// Notes -> events for eventsToKern: cut wherever a note starts or ends.
// tied: pitches that go on sounding from the event before.
export function notesToEvents(notes, grid) {
  const spans = notes.map((n) => ({ pitch: n.pitch, start: Math.round(n.on * grid.res), end: Math.round(n.off * grid.res) }));
  const cuts = [...new Set([0, grid.nCols, ...spans.flatMap((s) => [s.start, s.end])])].sort((a, b) => a - b);
  const events = [];
  for (let k = 0; k + 1 < cuts.length; k++) {
    const here = spans.filter((s) => s.start <= cuts[k] && s.end > cuts[k]);
    events.push({
      start: cuts[k],
      len: cuts[k + 1] - cuts[k],
      pitches: here.map((s) => s.pitch).sort((a, b) => a - b),
      tied: here.filter((s) => s.start < cuts[k]).map((s) => s.pitch).sort((a, b) => a - b),
    });
  }
  return events;
}

export function eventsToNotes(events, res) {
  const notes = [];
  for (const e of events) for (const p of e.pitches) notes.push({ pitch: p, on: e.start / res, off: (e.start + e.len) / res });
  return notes.sort((a, b) => a.on - b.on || a.pitch - b.pitch);
}

// kern pitch: c = C4, cc = C5, C = C3, CC = C2.
export function kernPitch(midi) {
  const name = NAMES[midi % 12];
  const octave = Math.floor(midi / 12) - 1;
  const letter = name[0];
  const accidental = name.length > 1 ? "#" : "";
  const repeat = octave >= 4 ? octave - 3 : 4 - octave;
  const base = octave >= 4 ? letter.toLowerCase() : letter;
  return base.repeat(repeat) + accidental;
}

// Durations kern can write as one token, in quarter notes, largest first.
const KERN_DURATIONS = [
  [6, "1."], [4, "1"], [3, "2."], [2, "2"], [1.5, "4."], [1, "4"],
  [0.75, "8."], [0.5, "8"], [0.375, "16."], [0.25, "16"], [0.125, "32"],
];

function splitDuration(quarters) {
  const parts = [];
  let left = quarters;
  while (left > EPS) {
    const fit = KERN_DURATIONS.find(([q]) => q <= left + EPS);
    if (!fit) break;
    parts.push(fit);
    left -= fit[0];
  }
  return parts;
}

// Events (from gridToEvents or notesToEvents) -> a **kern score Verovio can render.
export function eventsToKern(events, grid) {
  const { res, meter, barCells } = grid;
  const sounding = events.flatMap((e) => e.pitches);
  const sorted = [...sounding].sort((a, b) => a - b);
  const median = sorted.length ? sorted[Math.floor(sorted.length / 2)] : 60;
  const lines = ["**kern", median < 57 ? "*clefF4" : "*clefG2", `*M${meter.count}/${meter.unit}`];
  // Cut each event at bar lines, then into writable durations.
  const pieces = [];
  events.forEach((e, k) => {
    const tiedIn = e.tied || [];
    const tiedOut = events[k + 1]?.tied || [];
    let start = e.start;
    const end = e.start + e.len;
    const chunks = [];
    while (start < end) {
      const barEnd = (Math.floor(start / barCells) + 1) * barCells;
      const stop = Math.min(end, barEnd);
      for (const [q, recip] of splitDuration((stop - start) / res)) chunks.push({ recip, start, bar: Math.floor(start / barCells) });
      start = stop;
    }
    chunks.forEach((c, j) => pieces.push({ ...c, pitches: e.pitches, first: j === 0, last: j === chunks.length - 1, tiedIn, tiedOut }));
  });
  let bar = -1;
  for (const piece of pieces) {
    if (piece.bar !== bar) {
      bar = piece.bar;
      lines.push(`=${bar + 1}`);
    }
    if (!piece.pitches.length) {
      lines.push(`${piece.recip}r`);
      continue;
    }
    const tokens = piece.pitches.map((p) => {
      const token = piece.recip + kernPitch(p);
      const into = !piece.first || piece.tiedIn.includes(p);
      const onward = !piece.last || piece.tiedOut.includes(p);
      return into && onward ? token + "_" : onward ? "[" + token : into ? token + "]" : token;
    });
    lines.push(tokens.join(" "));
  }
  lines.push("==", "*-");
  return lines.join("\n") + "\n";
}

// Compare two note lists: same pitches at the same times?
export function compareNotes(before, after) {
  const key = (n) => `${n.pitch}@${n.on}-${n.off}`;
  const afterKeys = new Set(after.map(key));
  const beforeKeys = new Set(before.map(key));
  return {
    kept: before.filter((n) => afterKeys.has(key(n))).length,
    missing: before.filter((n) => !afterKeys.has(key(n))),
    added: after.filter((n) => !beforeKeys.has(key(n))),
  };
}
