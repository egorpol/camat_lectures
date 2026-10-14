// Input checks before Verovio sees the text, and melody checks for Demo D.
// Pure functions, no DOM. The notebooks carry the same rules in Python.

import { pitchName } from "./grid.js";

// Some broken inputs crash Verovio 6.3 instead of giving an error, and some
// valid ones are misread (tested 2026-10-14). errors: do not load the text;
// warnings: load it, but say what Verovio will get wrong.
export function precheck(format, text) {
  const problems = [];
  const warnings = [];
  if (format === "abc") {
    const lines = text.split(/\r?\n/);
    if (!lines.some((l) => /^X:/.test(l))) problems.push("ABC needs an X: line (for example X:1) before the tune.");
    if (!lines.some((l) => /^K:/.test(l))) problems.push("ABC needs a K: line (the key, for example K:C) before the notes.");
    let depth = 0;
    let unmatched = false;
    let chordLength = false;
    for (const line of lines) {
      if (/^[A-Za-z]:/.test(line)) continue; // header and lyrics lines
      const body = line.replace(/%.*$/, "").replace(/"[^"]*"/g, "").replace(/\|\]|\[\|/g, "|");
      if (/\][\d/]/.test(body)) chordLength = true;
      for (const ch of body) {
        if (ch === "[") depth++;
        if (ch === "]") {
          if (depth === 0) unmatched = true;
          else depth--;
        }
      }
    }
    if (unmatched) problems.push("There is a ] without a matching [ in the notes. Use |] for a final bar line.");
    if (chordLength) warnings.push("Verovio 6.3 ignores a length written after a chord, as in [CEG]2, and plays it as one unit. Write the length inside: [C2E2G2].");
  }
  if (format === "humdrum") {
    const lines = text.split(/\r?\n/).filter((l) => l && !l.startsWith("!!"));
    const head = lines.find((l) => l.startsWith("**"));
    if (head && / {2,}|\*\*\w+ +\*\*/.test(head) && !head.includes("\t")) {
      problems.push("Humdrum columns (spines) must be separated by tabs, not spaces.");
    }
    const manipulators = lines.some((l) => l.split("\t").some((t) => /^\*[\^v+x]$/.test(t)));
    if (head && !manipulators) {
      const width = head.split("\t").length;
      const bad = lines.findIndex((l) => l.split("\t").length !== width);
      if (bad >= 0) problems.push(`Line "${lines[bad]}" has ${lines[bad].split("\t").length} column(s), but the file has ${width}. Every line needs one entry per spine.`);
    }
  }
  return { errors: problems, warnings };
}

// LLM answers often come inside a Markdown code fence: keep only its content.
export function cleanAnswer(text) {
  const fence = text.match(/```[\w-]*\n([\s\S]*?)```/);
  return (fence ? fence[1] : text).trim() + "\n";
}

// Bar lengths in quarter notes, from the timemap's measure starts.
export function barLengths(timemap, notes) {
  const starts = timemap.filter((e) => e.measureOn).map((e) => e.qstamp);
  const end = Math.max(0, ...timemap.map((e) => e.qstamp), ...notes.map((n) => n.off));
  return starts.map((s, i) => (i + 1 < starts.length ? starts[i + 1] : end) - s);
}

export function parsePitch(name) {
  const m = /^([A-Ga-g])([#b]?)(-?\d)$/.exec(name.trim());
  if (!m) return null;
  const step = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 }[m[1].toLowerCase()];
  return 12 * (+m[3] + 1) + step + (m[2] === "#" ? 1 : m[2] === "b" ? -1 : 0);
}

// Compare what Verovio understood with what the prompt asked for.
// found: {meter, fifths, bars: [lengths], notes}; spec: {meter, fifths, bars, low, high, final}
export function melodyChecks(found, spec) {
  const checks = [];
  const add = (label, ok, detail) => checks.push({ label, ok, detail });
  const want = (spec.meter.count * 4) / spec.meter.unit;
  add(`Metre is ${spec.meter.count}/${spec.meter.unit}`, found.meter.count === spec.meter.count && found.meter.unit === spec.meter.unit, `found ${found.meter.count}/${found.meter.unit}`);
  add(`${spec.bars} bars`, found.bars.length === spec.bars, `found ${found.bars.length}`);
  const wrong = found.bars.map((q, i) => [i + 1, q]).filter(([, q]) => Math.abs(q - want) > 1e-6);
  add(`Every bar adds up to ${want} quarter notes`, wrong.length === 0, wrong.length ? wrong.map(([b, q]) => `bar ${b}: ${q}`).join(", ") : "all bars complete");
  const sig = (f) => (f === 0 ? "no sharps or flats" : f > 0 ? `${f} sharp${f > 1 ? "s" : ""}` : `${-f} flat${f < -1 ? "s" : ""}`);
  add(`Key signature: ${sig(spec.fifths)}`, found.fifths === spec.fifths, `found ${sig(found.fifths)}`);
  if (found.notes.length) {
    const pitches = found.notes.map((n) => n.pitch);
    const low = Math.min(...pitches);
    const high = Math.max(...pitches);
    add(`Range within ${pitchName(spec.low)}–${pitchName(spec.high)}`, low >= spec.low && high <= spec.high, `found ${pitchName(low)}–${pitchName(high)}`);
    const last = found.notes[found.notes.length - 1].pitch;
    add(`Ends on ${pitchName(spec.final).replace(/-?\d+$/, "")}`, last % 12 === spec.final % 12, `last note ${pitchName(last)}`);
  } else {
    add("Has notes", false, "Verovio found no notes");
  }
  return checks;
}
