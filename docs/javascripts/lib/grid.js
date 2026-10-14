// Melody <-> binary pitch x time grid (Demo C). Pure functions, no DOM.
// The Python version in 01_binary_grid.ipynb follows the same rules.
//
// A cell covers [i / res, (i + 1) / res) quarter notes. A note fills every
// cell whose start lies inside the note. Notes that cover no cell start are lost.

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

export function toGrid(notes, { res, meter }) {
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
  for (const n of notes) {
    const first = Math.ceil(n.on * res - EPS);
    const stop = Math.ceil(n.off * res - EPS); // first cell not covered
    if (first >= stop) {
      lost.push(n);
      continue;
    }
    for (let i = first; i < stop && i < nCols; i++) occ[n.pitch][i] = 1;
    ons[n.pitch][first] = 1;
  }
  return { res, meter, barCells, nCols, low, high, occ, ons, lost };
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
  return `Sounding (1 = the pitch sounds):\n${block(grid.occ)}\n\nOnsets (1 = a note starts):\n${block(grid.ons)}`;
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

// Events (from gridToEvents) -> a **kern score Verovio can render.
export function eventsToKern(events, grid) {
  const { res, meter, barCells } = grid;
  const sounding = events.flatMap((e) => e.pitches);
  const sorted = [...sounding].sort((a, b) => a - b);
  const median = sorted.length ? sorted[Math.floor(sorted.length / 2)] : 60;
  const lines = ["**kern", median < 57 ? "*clefF4" : "*clefG2", `*M${meter.count}/${meter.unit}`];
  // Cut each event at bar lines, then into writable durations.
  const pieces = [];
  for (const e of events) {
    let start = e.start;
    const end = e.start + e.len;
    const chunks = [];
    while (start < end) {
      const barEnd = (Math.floor(start / barCells) + 1) * barCells;
      const stop = Math.min(end, barEnd);
      for (const [q, recip] of splitDuration((stop - start) / res)) chunks.push({ recip, start, bar: Math.floor(start / barCells) });
      start = stop;
    }
    chunks.forEach((c, k) => pieces.push({ ...c, pitches: e.pitches, tie: chunks.length === 1 ? "" : k === 0 ? "[" : k === chunks.length - 1 ? "]" : "_" }));
  }
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
      if (piece.tie === "[") return "[" + token;
      return token + piece.tie;
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
