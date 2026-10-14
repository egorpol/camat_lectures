#!/usr/bin/env node
// Run the JS helpers on a JSON list of cases from stdin; print results as JSON.
// Case: { "fn": "<snake_case name>", "args": [...] }
// pitches maps arrive as plain objects; grids may carry occ/ons as arrays.

import { readFileSync } from "fs";
import { pitchesFromMEI, meterFromMEI, fifthsFromMEI } from "../../docs/javascripts/lib/mei.js";
import {
  pitchName, isBlackKey, notesFromTimemap, barQuarters, toGrid, gridRows,
  gridToText, gridToEvents, eventsToNotes, kernPitch, eventsToKern, compareNotes,
} from "../../docs/javascripts/lib/grid.js";
import { precheck, cleanAnswer, barLengths, parsePitch, melodyChecks } from "../../docs/javascripts/lib/checks.js";

const FN = {
  pitches_from_mei: pitchesFromMEI,
  meter_from_mei: meterFromMEI,
  fifths_from_mei: fifthsFromMEI,
  pitch_name: pitchName,
  is_black_key: isBlackKey,
  notes_from_timemap: notesFromTimemap,
  bar_quarters: barQuarters,
  to_grid: (notes, res, meter) => toGrid(notes, { res, meter }),
  grid_rows: (grid, compact) => gridRows(normalizeGrid(grid), compact),
  grid_to_text: (grid, compact, onsets) => gridToText(normalizeGrid(grid), { compact, onsets }),
  grid_to_events: (grid, onsets) => gridToEvents(normalizeGrid(grid), { onsets }),
  events_to_notes: eventsToNotes,
  kern_pitch: kernPitch,
  events_to_kern: (events, grid) => eventsToKern(events, normalizeGrid(grid)),
  compare_notes: compareNotes,
  precheck,
  clean_answer: cleanAnswer,
  bar_lengths: barLengths,
  parse_pitch: parsePitch,
  melody_checks: melodyChecks,
};

function normalizeGrid(grid) {
  if (!grid) return grid;
  const occ = {};
  const ons = {};
  for (const [k, v] of Object.entries(grid.occ || {})) occ[k] = Uint8Array.from(v);
  for (const [k, v] of Object.entries(grid.ons || {})) ons[k] = Uint8Array.from(v);
  return { ...grid, occ, ons, low: +grid.low, high: +grid.high, barCells: +grid.barCells, nCols: +grid.nCols, res: +grid.res };
}

function serialize(value) {
  if (value instanceof Map) return Object.fromEntries(value);
  if (value instanceof Uint8Array) return Array.from(value);
  if (Array.isArray(value)) return value.map(serialize);
  if (value && typeof value === "object") {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = serialize(v);
    return out;
  }
  return value;
}

const cases = JSON.parse(readFileSync(0, "utf8"));
const results = cases.map((c) => {
  const fn = FN[c.fn];
  if (!fn) throw new Error("unknown fn: " + c.fn);
  let args = c.args;
  if (c.fn === "notes_from_timemap") {
    args = [args[0], new Map(Object.entries(args[1]).map(([k, v]) => [k, v]))];
  }
  return serialize(fn(...args));
});
process.stdout.write(JSON.stringify(results));
