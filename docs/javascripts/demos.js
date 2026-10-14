// Live demos for the session pages. Each demo is a <div data-demo="...">
// placeholder in the Markdown; this script builds its controls.
//   formats  Demo B: one text box per format, rendered by Verovio
//   roll     Demo A: player-piano roll from MIDI fetched at runtime
//   grid     Demo C: melody -> 0/1 grid -> notes
//   llm      Demo D: check an LLM-written melody
//   facsimile Demo E: MEI measure zones on a scan, linked to the rendering

import { readScore, verovioReady, VEROVIO_VERSION } from "./lib/vrv.js";
import { parseMidi } from "./lib/midi.js";
import { drawRoll, TRACK_COLORS } from "./lib/roll.js";
import * as G from "./lib/grid.js";
import { cleanAnswer, barLengths, melodyChecks, parsePitch } from "./lib/checks.js";
import { facsimileFromMEI, iiifUrl, zoneRegion } from "./lib/facs.js";

// ---------------------------------------------------------------- helpers

function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v === true) el.setAttribute(k, "");
    else el.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

function debounce(fn, ms = 400) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

const bytes = (text) => new TextEncoder().encode(text).length;
const fmt = (n) => n.toLocaleString("en-US");

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.text();
}

// Score + messages into a box. Returns the readScore result.
function showScore(box, result, { emptyNote = "" } = {}) {
  box.replaceChildren();
  if (result.svg) box.append(h("div", { class: "vrv-score" }));
  if (result.svg) box.firstChild.innerHTML = result.svg;
  else if (emptyNote) box.append(h("p", { class: "vrv-note" }, emptyNote));
  const lines = [
    ...result.errors.map((t) => ["error", t]),
    ...result.warnings.map((t) => ["warning", t]),
    ...result.log.split("\n").filter(Boolean).map((t) => ["log", t]),
  ];
  if (lines.length) {
    box.append(h("ul", { class: "vrv-messages" }, lines.map(([kind, t]) => h("li", { class: `vrv-${kind}` }, t))));
  }
  return result;
}

function loadingNote() {
  return h("p", { class: "vrv-note" }, `Loading Verovio ${VEROVIO_VERSION} (about 12 MB, once per visit)…`);
}

// ---------------------------------------------------------------- Demo B

const FORMATS = [
  { name: "ABC", input: "abc", file: "alle_meine_entchen.abc", rows: 7 },
  { name: "Humdrum **kern", input: "humdrum", file: "alle_meine_entchen.krn", rows: 12 },
  { name: "Plaine & Easie", input: "pae", file: "alle_meine_entchen.pae", rows: 4 },
  { name: "EsAC", input: "esac", file: "alle_meine_entchen.esac", rows: 6 },
  { name: "MusicXML", input: "xml", file: "alle_meine_entchen.musicxml", rows: 14 },
  { name: "MEI", input: "mei", file: "alle_meine_entchen.mei", rows: 14 },
  { name: "GABC (chant, extra)", input: "gabc", file: "alleluia_fragment.gabc", rows: 2 },
];

async function initFormats(root) {
  const base = root.dataset.examples || "examples/";
  root.replaceChildren(loadingNote());
  const cards = [];
  for (const f of FORMATS) {
    const original = await fetchText(base + f.file).catch((e) => `Could not load ${f.file}: ${e.message}`);
    const textarea = h("textarea", { rows: f.rows, spellcheck: "false", "aria-label": `${f.name} text` });
    textarea.value = original;
    const size = h("span", { class: "vrv-size" });
    const out = h("div", { class: "vrv-out" });
    const mei = h("pre", { class: "vrv-mei", hidden: true });
    const roll = h("canvas", { class: "vrv-roll vrv-roll-small", hidden: true });
    let last = null;
    const render = async () => {
      size.textContent = `${fmt(bytes(textarea.value))} bytes`;
      last = showScore(out, await readScore(f.input, textarea.value, { width: out.clientWidth || 500, scale: 35 }));
      if (!mei.hidden) mei.textContent = last.mei;
      if (!roll.hidden) drawSmallRoll(roll, last);
    };
    const card = h(
      "section",
      { class: "vrv-card" },
      h("header", {}, h("strong", {}, f.name), " ", h("code", {}, `inputFrom: "${f.input}"`), " ", size),
      h("div", { class: "vrv-card-body" }, textarea, out),
      h(
        "div",
        { class: "vrv-actions" },
        h("button", { type: "button", class: "md-button", onclick: () => {
          mei.hidden = !mei.hidden;
          if (!mei.hidden && last) mei.textContent = last.mei;
        } }, "Show as MEI"),
        h("button", { type: "button", class: "md-button", onclick: () => {
          roll.hidden = !roll.hidden;
          if (!roll.hidden && last) drawSmallRoll(roll, last);
        } }, "Piano roll"),
        h("button", { type: "button", class: "md-button", onclick: () => {
          textarea.value = original;
          render();
        } }, "Reset"),
      ),
      roll,
      mei,
    );
    textarea.addEventListener("input", debounce(render));
    cards.push({ card, render });
  }
  root.replaceChildren(...cards.map((c) => c.card));
  await verovioReady();
  for (const c of cards) await c.render();
}

function drawSmallRoll(canvas, result) {
  const notes = result.notes.map((n) => ({ pitch: n.pitch, start: n.on, end: n.off, track: 0 }));
  if (!notes.length) {
    canvas.hidden = true;
    return;
  }
  drawRoll(canvas, notes, { from: 0, timeLabel: (t) => `${t} q`, timeStep: (result.meter?.count * 4) / (result.meter?.unit || 4) || 4 });
}

// ---------------------------------------------------------------- Demo A

const ROLE = {
  raw: { 1: ["bass holes", 0], 2: ["treble holes", 1], 3: ["bass expression holes", 2], 4: ["treble expression holes", 3] },
  exp: { 1: ["bass notes", 0], 2: ["treble notes", 1] },
};

function pedalBands(track) {
  const bands = [];
  for (const [control, row, color, label] of [[64, 0, "#2ca02c", "sustain pedal"], [67, 1, "#8c564b", "soft pedal"]]) {
    let down = null;
    for (const c of track.controls.filter((c) => c.control === control)) {
      if (c.value >= 64 && down === null) down = c.time;
      if (c.value < 64 && down !== null) {
        bands.push({ start: down, end: c.time, row, color, label });
        down = null;
      }
    }
  }
  return bands;
}

async function initRoll(root) {
  const urls = { exp: root.dataset.exp, raw: root.dataset.raw };
  const status = h("p", { class: "vrv-note" });
  const loadButton = h("button", { type: "button", class: "md-button md-button--primary" }, "Load the roll (two MIDI files from GitHub)");
  root.replaceChildren(h("div", { class: "vrv-actions" }, loadButton), status);

  loadButton.addEventListener("click", async () => {
    loadButton.disabled = true;
    status.textContent = "Downloading…";
    let files;
    try {
      const [exp, raw] = await Promise.all(
        [urls.exp, urls.raw].map(async (u) => {
          const r = await fetch(u);
          if (!r.ok) throw new Error(`${u}: HTTP ${r.status}`);
          return parseMidi(await r.arrayBuffer());
        }),
      );
      files = { exp, raw };
    } catch (e) {
      status.textContent = `Could not load the MIDI files (${e.message}). Check the network, or use the notebook.`;
      loadButton.disabled = false;
      return;
    }
    loadButton.remove();
    buildRollViewer(root, files, status);
  });
}

function buildRollViewer(root, files, status) {
  const versions = {};
  for (const key of ["exp", "raw"]) {
    const notes = [];
    for (const t of files[key].tracks) {
      const role = ROLE[key][t.index];
      if (!role) continue;
      for (const n of t.notes) notes.push({ ...n, track: role[1] });
    }
    notes.sort((a, b) => a.start - b.start);
    const pedalTrack = files[key].tracks.find((t) => t.controls.some((c) => c.control === 64));
    const velocities = notes.map((n) => n.velocity);
    versions[key] = {
      notes,
      duration: files[key].duration,
      bands: pedalTrack ? pedalBands(pedalTrack) : [],
      soft: Math.min(...velocities),
      loud: Math.max(...velocities),
    };
  }

  const state = { version: "exp", start: 4, length: 20, speed: 1, playhead: null };
  const canvas = h("canvas", { class: "vrv-roll vrv-roll-large" });
  const legend = h("div", { class: "vrv-legend" });
  const slider = h("input", { type: "range", min: 0, step: 0.5, value: state.start, "aria-label": "Start time in seconds" });
  const startLabel = h("span", { class: "vrv-size" });
  const lengthSelect = h("select", { "aria-label": "Window length" }, [5, 10, 20, 40, 80, 160].map((s) => h("option", { value: s, selected: s === state.length }, `${s} s`)));
  const versionSelect = h("select", { "aria-label": "MIDI version" },
    h("option", { value: "exp" }, "expressive: holes merged into notes"),
    h("option", { value: "raw" }, "raw: one event per hole"));
  const speedSlider = h("input", { type: "range", min: 0.25, max: 2, step: 0.25, value: state.speed, "aria-label": "Playback speed" });
  const speedLabel = h("span", { class: "vrv-size" }, "1×");
  const playButton = h("button", { type: "button", class: "md-button" }, "▶ Play window");
  const info = h("p", { class: "vrv-note" });

  const draw = () => {
    const v = versions[state.version];
    slider.max = Math.max(0, Math.floor(v.duration - state.length));
    startLabel.textContent = `${state.start.toFixed(1)}–${(state.start + state.length).toFixed(1)} s`;
    const visible = v.notes.filter((n) => n.end >= state.start && n.start <= state.start + state.length);
    const raw = state.version === "raw";
    drawRoll(canvas, visible, {
      from: state.start,
      to: state.start + state.length,
      low: raw ? 14 : 21,
      high: raw ? 114 : 108,
      color: (n) => TRACK_COLORS[n.track],
      // Expressive file: the softest note in the file is pale, the loudest solid.
      alpha: (n) => (raw ? 0.9 : 0.3 + (0.7 * (n.velocity - v.soft)) / Math.max(1, v.loud - v.soft)),
      timeLabel: (t) => `${t} s`,
      timeStep: state.length <= 10 ? 1 : state.length <= 40 ? 5 : state.length <= 80 ? 10 : 20,
      bands: raw ? [] : v.bands,
      playhead: state.playhead,
    });
    const total = v.notes.length;
    info.textContent = raw
      ? `Raw file: ${fmt(total)} hole events in 4 tracks, ${v.duration.toFixed(0)} s. In this window: ${fmt(visible.length)}.`
      : `Expressive file: ${fmt(total)} notes in 2 tracks, ${v.duration.toFixed(0)} s. In this window: ${fmt(visible.length)}. `
        + `The shade of a note is its loudness (MIDI velocity, decoded from the expression holes): pale = soft, solid = loud.`;
    const roles = Object.values(ROLE[state.version]);
    legend.replaceChildren(
      ...roles.map(([label, i]) => h("span", {}, h("i", { style: `background:${TRACK_COLORS[i]}` }), label)),
      ...(raw ? [] : [
        h("span", {}, h("i", { class: "vrv-ramp" }), `soft → loud (velocity ${v.soft}–${v.loud})`),
        h("span", {}, h("i", { style: "background:#2ca02c" }), "sustain pedal"),
        h("span", {}, h("i", { style: "background:#8c564b" }), "soft pedal"),
      ]),
    );
  };

  slider.addEventListener("input", () => {
    state.start = +slider.value;
    draw();
  });
  lengthSelect.addEventListener("change", () => {
    state.length = +lengthSelect.value;
    draw();
  });
  versionSelect.addEventListener("change", () => {
    state.version = versionSelect.value;
    draw();
  });
  speedSlider.addEventListener("input", () => {
    state.speed = +speedSlider.value;
    speedLabel.textContent = `${state.speed}×`;
    player?.setSpeed(state.speed);
  });

  let player = null;
  playButton.addEventListener("click", () => {
    if (player) {
      player.stop();
      return;
    }
    player = playWindow(versions[state.version].notes, state.start, state.length, state.version === "raw", state.speed, (t) => {
      state.playhead = t;
      draw();
    }, () => {
      player = null;
      state.playhead = null;
      playButton.textContent = "▶ Play window";
      draw();
    });
    playButton.textContent = "■ Stop";
  });

  root.replaceChildren(
    h("div", { class: "vrv-controls" },
      h("label", {}, "Version ", versionSelect),
      h("label", {}, "Window ", lengthSelect),
      h("label", { class: "vrv-grow" }, "Start ", slider, " ", startLabel),
      h("label", {}, "Speed ", speedSlider, " ", speedLabel),
      playButton),
    canvas,
    legend,
    info,
  );
  status.remove();
  draw();
  new ResizeObserver(debounce(draw, 100)).observe(canvas);
}

// A very plain synthesiser: enough to hear rhythm, chords and dynamics.
// speed: seconds of roll per second of sound; setSpeed() changes it while playing.
function playWindow(notes, start, length, raw, speed, onTime, onEnd) {
  const ctx = new AudioContext();
  const master = ctx.createGain();
  master.gain.value = 0.5;
  const limiter = ctx.createDynamicsCompressor();
  master.connect(limiter).connect(ctx.destination);
  const queue = notes.filter((n) => n.start >= start && n.start < start + length && n.pitch >= 21 && n.pitch <= 108);
  // Roll time `from` is heard at audio time `anchor`; after that the roll advances `speed` times as fast.
  let anchor = ctx.currentTime + 0.1;
  let from = start;
  const rollTime = (audio) => from + (audio - anchor) * speed;
  let next = 0;
  let waiting = []; // oscillators that have not started yet
  let stopped = false;

  const schedule = () => {
    const now = ctx.currentTime;
    waiting = waiting.filter((w) => w.at > now);
    const horizon = rollTime(now + 1.0);
    while (next < queue.length && queue[next].start < horizon) {
      const n = queue[next++];
      const at = anchor + (n.start - from) / speed;
      const dur = (Math.min(n.end, start + length) - n.start) / speed;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.value = 440 * 2 ** ((n.pitch - 69) / 12);
      const level = raw ? 0.12 : 0.04 + (0.2 * Math.max(0, n.velocity - 20)) / 60;
      gain.gain.setValueAtTime(0, at);
      gain.gain.linearRampToValueAtTime(level, at + 0.005);
      gain.gain.setTargetAtTime(level * 0.3, at + 0.01, 0.4);
      gain.gain.setTargetAtTime(0, at + Math.max(0.02, dur), 0.05);
      osc.connect(gain).connect(master);
      osc.start(at);
      osc.stop(at + Math.max(0.02, dur) + 0.4);
      waiting.push({ osc, at });
    }
  };
  schedule();
  const timer = setInterval(schedule, 200);
  const frame = () => {
    if (stopped) return;
    const t = rollTime(ctx.currentTime);
    if (t > start + length + 0.5 * speed) {
      stop();
      return;
    }
    onTime(Math.max(start, t));
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);

  function stop() {
    if (stopped) return;
    stopped = true;
    clearInterval(timer);
    ctx.close();
    onEnd();
  }

  // Notes already sounding keep their length; the ones not yet started are scheduled again.
  function setSpeed(value) {
    const now = Math.max(ctx.currentTime, anchor);
    from = rollTime(now);
    anchor = now;
    speed = value;
    for (const w of waiting) w.osc.disconnect();
    waiting = [];
    next = queue.findIndex((n) => n.start >= from);
    if (next < 0) next = queue.length;
    schedule();
  }
  return { stop, setSpeed };
}

// ---------------------------------------------------------------- Demo C

async function initGrid(root) {
  const base = root.dataset.examples || "examples/";
  const original = await fetchText(base + "alle_meine_entchen.abc").catch(() => "X:1\nT:Alle meine Entchen\nM:4/4\nL:1/4\nK:C\nC D E F | G2 G2 | A A A A | G4 |]\n");
  const textarea = h("textarea", { rows: 7, spellcheck: "false", "aria-label": "Melody in ABC" });
  textarea.value = original;
  const resSelect = h("select", { "aria-label": "Grid cell" },
    h("option", { value: 1 }, "quarter note"),
    h("option", { value: 2 }, "eighth note"),
    h("option", { value: 4 }, "sixteenth note"));
  const onsetBox = h("input", { type: "checkbox" });
  const compactBox = h("input", { type: "checkbox", checked: true });
  const before = h("div", { class: "vrv-out" }, loadingNote());
  const after = h("div", { class: "vrv-out" });
  const table = h("div", { class: "grid-wrap" });
  const text = h("pre", { class: "grid-text" });
  const kernPre = h("pre", { class: "vrv-mei" });
  const summary = h("div", { class: "grid-summary" });
  const state = { source: null, grid: null };

  root.replaceChildren(
    h("div", { class: "vrv-card-body" },
      h("div", {}, h("p", { class: "vrv-label" }, "Melody (ABC, edit me)"), textarea,
        h("div", { class: "vrv-controls" },
          h("label", {}, "Grid cell ", resSelect),
          h("label", {}, onsetBox, " keep an onset grid"),
          h("label", {}, compactBox, " hide empty black-key rows"),
          h("button", { type: "button", class: "md-button", onclick: () => { textarea.value = original; fromMelody(); } }, "Reset"))),
      h("div", {}, h("p", { class: "vrv-label" }, "Original, rendered by Verovio"), before)),
    h("p", { class: "vrv-label" }, "The grid: one row per pitch, one column per cell. Click a cell to change it."),
    table,
    summary,
    h("div", { class: "vrv-card-body" },
      h("div", {}, h("p", { class: "vrv-label" }, "The grid as text"), text),
      h("div", {}, h("p", { class: "vrv-label" }, "Back from the grid to notes"), after)),
    h("details", {}, h("summary", {}, "The **kern that the page writes from the grid"), kernPre),
  );

  const fromMelody = async () => {
    const result = await readScore("abc", textarea.value, { width: before.clientWidth || 400, scale: 28, header: "none" });
    showScore(before, result);
    if (!result.ok || !result.notes.length) {
      state.source = null;
      table.replaceChildren();
      summary.textContent = result.ok ? "Verovio found no notes." : "";
      return;
    }
    state.source = result;
    buildGrid();
  };

  const buildGrid = () => {
    if (!state.source) return;
    state.grid = G.toGrid(state.source.notes, { res: +resSelect.value, meter: state.source.meter });
    fromGrid();
  };

  const fromGrid = async () => {
    const grid = state.grid;
    const onsets = onsetBox.checked;
    drawGridTable(table, grid, { onsets, compact: compactBox.checked, onChange: fromGrid });
    text.textContent = G.gridToText(grid, { compact: compactBox.checked, onsets });
    const events = G.gridToEvents(grid, { onsets });
    const kern = G.eventsToKern(events, grid);
    kernPre.textContent = kern;
    showScore(after, await readScore("humdrum", kern, { width: after.clientWidth || 400, scale: 28, header: "none" }));
    const back = G.eventsToNotes(events, grid.res);
    const cmp = G.compareNotes(state.source.notes, back);
    const n = state.source.notes.length;
    const items = [
      `The melody has ${n} notes. Read back from the grid: ${back.length} notes, ${cmp.kept} of them unchanged.`,
    ];
    if (grid.lost.length) {
      items.push(`${grid.lost.length} note(s) start and end inside one cell and disappear: ${grid.lost.map((x) => G.pitchName(x.pitch)).join(", ")}. Try a smaller cell.`);
    }
    if (cmp.kept === n && back.length === n) items.push("Nothing lost: the round trip gives back the same notes.");
    else if (!onsets) items.push("Repeated notes of the same pitch merge into one long note. Tick “keep an onset grid” to keep them apart.");
    summary.replaceChildren(...items.map((t) => h("p", {}, t)));
  };

  textarea.addEventListener("input", debounce(fromMelody, 500));
  resSelect.addEventListener("change", buildGrid);
  onsetBox.addEventListener("change", fromGrid);
  compactBox.addEventListener("change", fromGrid);
  await fromMelody();
}

function drawGridTable(container, grid, { onsets, compact, onChange }) {
  const rows = G.gridRows(grid, compact);
  const bars = grid.nCols / grid.barCells;
  const head = h("tr", {}, h("th", {}), Array.from({ length: bars }, (_, b) => h("th", { colspan: grid.barCells, class: "bar" }, `bar ${b + 1}`)));
  const body = rows.map((p) =>
    h("tr", {}, h("th", { class: "pitch" }, G.pitchName(p)),
      Array.from({ length: grid.nCols }, (_, i) => {
        const on = grid.occ[p][i];
        const attack = onsets && on && grid.ons[p][i];
        const cell = h("td", {
          class: [on ? "on" : "", attack ? "onset" : "", i % grid.barCells === 0 ? "barstart" : ""].join(" ").trim(),
          title: `${G.pitchName(p)}, cell ${i + 1}`,
        }, attack ? "2" : on ? "1" : "0");
        cell.addEventListener("click", () => {
          if (!onsets) {
            grid.occ[p][i] = on ? 0 : 1;
            grid.ons[p][i] = on ? 0 : grid.occ[p][i - 1] ? 0 : 1;
          } else if (!on) {
            grid.occ[p][i] = 1;
            grid.ons[p][i] = 1;
          } else if (attack) {
            grid.ons[p][i] = 0;
          } else {
            grid.occ[p][i] = 0;
            grid.ons[p][i] = 0;
          }
          onChange();
        });
        return cell;
      })));
  container.replaceChildren(h("table", { class: "grid-table" }, h("thead", {}, head), h("tbody", {}, body)));
  container.append(h("p", { class: "vrv-note" }, onsets
    ? "Click cycles: 0 → 2 (a note starts, dark) → 1 (it continues, light) → 0."
    : "Click switches a cell between 0 and 1."));
}

// ---------------------------------------------------------------- Demo D

async function initLLM(root) {
  const data = await fetch(root.dataset.answers).then((r) => r.json()).catch(() => null);
  if (!data) {
    root.replaceChildren(h("p", { class: "vrv-error" }, "Could not load the recorded answers."));
    return;
  }
  const spec = data.spec;
  const field = (label, value, size = 4) => {
    const input = h("input", { type: "text", value, size, "aria-label": label });
    return [input, h("label", {}, label + " ", input)];
  };
  const [meterIn, meterLabel] = field("Metre", spec.meter.join("/"));
  const [barsIn, barsLabel] = field("Bars", String(spec.bars), 3);
  const keySelect = h("select", { "aria-label": "Key signature" },
    Array.from({ length: 15 }, (_, i) => i - 7).map((f) =>
      h("option", { value: f, selected: f === spec.fifths }, f === 0 ? "no sharps/flats" : f > 0 ? `${f} sharp${f > 1 ? "s" : ""}` : `${-f} flat${f < -1 ? "s" : ""}`)));
  const [lowIn, lowLabel] = field("Lowest", spec.low);
  const [highIn, highLabel] = field("Highest", spec.high);
  const [finalIn, finalLabel] = field("Ends on", spec.final.replace(/\d+$/, ""), 3);
  const formatSelect = h("select", { "aria-label": "Format" }, h("option", { value: "abc" }, "ABC"), h("option", { value: "humdrum" }, "**kern"));
  const textarea = h("textarea", { rows: 10, spellcheck: "false", placeholder: "Paste the LLM's answer here", "aria-label": "LLM answer" });
  const source = h("p", { class: "vrv-note" });
  const results = h("div", { class: "llm-results" });
  const out = h("div", { class: "vrv-out" });

  const check = async () => {
    const text = cleanAnswer(textarea.value);
    if (!text.trim()) return;
    const result = await readScore(formatSelect.value, text, { width: out.clientWidth || 600, scale: 35 });
    showScore(out, result);
    const [count, unit] = meterIn.value.split("/").map(Number);
    const want = {
      meter: { count, unit },
      bars: +barsIn.value,
      fifths: +keySelect.value,
      low: parsePitch(lowIn.value),
      high: parsePitch(highIn.value),
      final: parsePitch(finalIn.value.trim() + "4"),
    };
    const rows = [["Verovio reads it", result.ok, result.ok ? (result.log ? "with warnings, see below the score" : "no warnings") : result.errors.join(" ")]];
    if (result.ok) {
      const found = { meter: result.meter, fifths: result.fifths, bars: barLengths(result.timemap, result.notes), notes: result.notes };
      rows.push(...melodyChecks(found, want).map((c) => [c.label, c.ok, c.detail]));
    }
    results.replaceChildren(h("table", { class: "llm-checks" },
      h("tbody", {}, rows.map(([label, ok, detail]) => h("tr", { class: ok ? "ok" : "fail" }, h("td", {}, ok ? "✓" : "✗"), h("td", {}, label), h("td", {}, detail))))));
  };

  const answerButtons = data.answers.map((a) => h("button", { type: "button", class: "md-button", onclick: () => {
    textarea.value = a.text;
    formatSelect.value = a.format;
    source.textContent = a.source;
    check();
  } }, a.label));

  const copy = (text) => h("button", { type: "button", class: "md-button", onclick: (e) => {
    navigator.clipboard?.writeText(text);
    e.target.textContent = "Copied";
  } }, "Copy");

  root.replaceChildren(
    h("p", { class: "vrv-label" }, "1. The prompt"),
    h("div", { class: "llm-prompt" }, h("p", {}, data.prompt_abc), copy(data.prompt_abc)),
    h("div", { class: "llm-prompt" }, h("p", {}, "Follow-up: ", data.prompt_kern), copy(data.prompt_kern)),
    h("p", { class: "vrv-label" }, "2. What the prompt asks for (change it if you change the prompt)"),
    h("div", { class: "vrv-controls" }, meterLabel, barsLabel, h("label", {}, "Key signature ", keySelect), lowLabel, highLabel, finalLabel),
    h("p", { class: "vrv-label" }, "3. The answer"),
    h("div", { class: "vrv-controls" }, h("label", {}, "Format ", formatSelect), h("span", {}, "Recorded answers: "), answerButtons),
    source,
    textarea,
    h("div", { class: "vrv-actions" }, h("button", { type: "button", class: "md-button md-button--primary", onclick: check }, "Check and render")),
    results,
    out,
  );
}

// ---------------------------------------------------------------- Demo E

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}, text = "") {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (text) el.textContent = text;
  return el;
}

// Verovio: the whole page with the source's system breaks, then each bar alone.
async function renderFacsimilePage(text, measures) {
  const { module, esm } = await verovioReady();
  const tk = new esm.VerovioToolkit(module);
  try {
    tk.setOptions({
      inputFrom: "mei",
      breaks: "encoded",
      pageWidth: 2400,
      adjustPageHeight: true,
      systemDivider: "none",
      footer: "none",
      pageMarginTop: 30,
      pageMarginBottom: 30,
      pageMarginLeft: 30,
      pageMarginRight: 30,
    });
    if (!tk.loadData(text)) throw new Error("Verovio could not read the MEI file");
    const page = tk.renderToSVG(1);
    tk.setOptions({ breaks: "auto", pageWidth: 1100, header: "none" });
    const bars = measures.map((m) => {
      tk.select({ measureRange: `${m.n}-${m.n}` });
      tk.redoLayout();
      return tk.renderToSVG(1);
    });
    return { page, bars };
  } finally {
    tk.destroy?.();
  }
}

async function initFacsimile(root) {
  const base = root.dataset.examples || "examples/";
  root.replaceChildren(loadingNote());
  const text = await fetchText(base + root.dataset.mei);
  const { surface, measures } = facsimileFromMEI(text);
  const { page, bars } = await renderFacsimilePage(text, measures);
  const noted = measures.filter((m) => m.notes.length);

  // Source: the scan from the IIIF server, with one rectangle per zone.
  const img = h("img", {
    src: iiifUrl(surface.target, { size: "1000," }),
    width: 1000,
    height: Math.round((1000 * surface.height) / surface.width),
    alt: `Scan: ${root.dataset.title}`,
  });
  const overlay = svgEl("svg", { viewBox: `0 0 ${surface.width} ${surface.height}`, preserveAspectRatio: "none", class: "facs-zones" });
  const rects = measures.map((m, i) => {
    const { ulx, uly, lrx, lry } = m.zone;
    const r = svgEl("rect", { x: ulx, y: uly, width: lrx - ulx, height: lry - uly, class: "facs-zone" + (m.notes.length ? " has-note" : "") });
    r.dataset.i = i;
    r.append(svgEl("title", {}, `Bar ${m.n}`));
    overlay.append(r);
    return r;
  });
  const scan = h("div", { class: "facs-scan" }, img, overlay);
  img.addEventListener("error", () =>
    scan.replaceChildren(h("p", { class: "vrv-error" }, "The scan could not be loaded from the library's IIIF server. The encoding still works.")));

  // Encoding: Verovio's SVG keeps the MEI xml:ids, so each bar is g.measure#id.
  const render = h("div", { class: "vrv-score facs-render" });
  render.innerHTML = page;

  // One selected bar, enlarged: the zone cut out by the IIIF server, and the bar alone.
  const barLabel = h("strong", { "aria-live": "polite" });
  const code = h("p", { class: "facs-code" });
  const crop = h("img", { class: "facs-crop", alt: "" });
  const barRender = h("div", { class: "vrv-score facs-bar" });
  const notes = h("div", { class: "facs-notes" });
  const showAll = h("input", { type: "checkbox", checked: true, onchange: () => root.classList.toggle("facs-hide-zones", !showAll.checked) });

  let active = 0;
  let hover = -1;
  let groups = [];
  const paint = () => {
    rects.forEach((r, i) => {
      r.classList.toggle("is-active", i === active);
      r.classList.toggle("is-hover", i === hover);
    });
    groups.forEach((g, i) => {
      g?.classList.toggle("is-active", i === active);
      g?.classList.toggle("is-hover", i === hover);
    });
  };
  const markNotes = (box, m) => {
    for (const note of m.notes) for (const id of note.targets) box.querySelector(`[id="${id}"]`)?.classList.add("facs-target");
  };
  const select = (i) => {
    active = (i + measures.length) % measures.length;
    const m = measures[active];
    const z = m.zone;
    barLabel.textContent = `Bar ${m.n} of ${measures.length}`;
    code.replaceChildren(
      h("code", {}, `<measure n="${m.n}" facs="#${z.id}">`),
      " points to ",
      h("code", {}, `<zone xml:id="${z.id}" ulx="${z.ulx}" uly="${z.uly}" lrx="${z.lrx}" lry="${z.lry}"/>`),
    );
    crop.src = iiifUrl(surface.target, { region: zoneRegion(z, surface), size: "!840,840" });
    crop.alt = `Bar ${m.n} in the scan`;
    barRender.innerHTML = bars[active];
    markNotes(barRender, m);
    notes.replaceChildren(...m.notes.map((n) => h("p", {}, h("strong", {}, "Editorial note in the MEI (the note in blue): "), n.text)));
    paint();
  };
  const pick = (selector) => (e) => {
    const el = e.target.closest?.(selector);
    if (e.type === "click") el && select(+el.dataset.i);
    else {
      hover = el ? +el.dataset.i : -1;
      paint();
    }
  };
  for (const [box, selector] of [[overlay, "rect.facs-zone"], [render, "g.measure[data-i]"]]) {
    box.addEventListener("pointerover", pick(selector));
    box.addEventListener("pointerleave", pick("none"));
    box.addEventListener("click", pick(selector));
  }

  const pane = (body, caption) => h("div", { class: "facs-pane" }, body, h("p", { class: "vrv-note" }, caption));
  root.replaceChildren(
    h("div", { class: "facs-panes" },
      pane(scan, "Source: the scan, one zone per bar"),
      pane(render, "Encoding: the MEI rendered by Verovio, with the source's system breaks")),
    h("div", { class: "vrv-controls" },
      h("label", {}, showAll, "Show all zones"),
      h("span", { class: "vrv-note" },
        `${measures.length} bars, each linked to a zone on the page. Point at a bar in either view; click to select it.`,
        noted.length ? ` Bar ${noted.map((m) => m.n).join(", ")} has an editorial note (blue).` : "")),
    h("div", { class: "facs-detail" },
      h("div", { class: "vrv-controls" },
        h("button", { type: "button", class: "md-button", "aria-label": "Previous bar", onclick: () => select(active - 1) }, "◀"),
        barLabel,
        h("button", { type: "button", class: "md-button", "aria-label": "Next bar", onclick: () => select(active + 1) }, "▶")),
      code,
      h("div", { class: "facs-panes" }, pane(crop, "Scan: the zone, cut out by the IIIF server"), pane(barRender, "Encoding: the same bar")),
      notes),
  );

  // Hit areas need the SVG in the document (getBBox). We take the staves'
  // boxes only: Verovio 6.3 leaves some empty <harm> groups at the page
  // origin (bar 11 here), which would stretch the whole measure's box.
  const unionBox = (boxes) => {
    const x = Math.min(...boxes.map((b) => b.x));
    const y = Math.min(...boxes.map((b) => b.y));
    return {
      x,
      y,
      width: Math.max(...boxes.map((b) => b.x + b.width)) - x,
      height: Math.max(...boxes.map((b) => b.y + b.height)) - y,
    };
  };
  groups = measures.map((m, i) => {
    const g = render.querySelector(`g.measure[id="${m.id}"]`);
    if (!g) return null;
    const staves = [...g.querySelectorAll(":scope > g.staff")].map((s) => s.getBBox());
    const box = staves.length ? unionBox(staves) : g.getBBox();
    g.dataset.i = i;
    g.prepend(svgEl("rect", { x: box.x, y: box.y, width: box.width, height: box.height, class: "facs-hit" }));
    markNotes(g, m);
    return g;
  });
  select(0);
}

// ---------------------------------------------------------------- start

const DEMOS = { formats: initFormats, roll: initRoll, grid: initGrid, llm: initLLM, facsimile: initFacsimile };

for (const root of document.querySelectorAll("[data-demo]")) {
  const init = DEMOS[root.dataset.demo];
  if (!init) continue;
  init(root).catch((error) => {
    console.error(error);
    root.append(h("p", { class: "vrv-error" }, `This demo failed to start: ${error.message}`));
  });
}
