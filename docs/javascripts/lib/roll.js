// Draw a piano roll (time x pitch) on a canvas.
// notes: [{pitch, start, end, track?, velocity?}]; time unit is up to the caller.

import { pitchName, isBlackKey } from "./grid.js";

export const TRACK_COLORS = ["#1f77b4", "#d62728", "#9467bd", "#ff7f0e", "#2ca02c", "#8c564b"];

function cssVar(name, fallback) {
  const value = getComputedStyle(document.body).getPropertyValue(name).trim();
  return value || fallback;
}

export function drawRoll(canvas, notes, {
  from = 0,
  to = null,
  low = null,
  high = null,
  color = (n) => TRACK_COLORS[(n.track ?? 0) % TRACK_COLORS.length],
  alpha = () => 1,
  timeLabel = (t) => `${t}`,
  timeStep = 1,
  bands = [], // [{start, end, row: 0|1, color, label}] drawn in a strip below the roll
  playhead = null,
} = {}) {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);

  const end = to ?? Math.max(from + 1, ...notes.map((n) => n.end));
  const pitches = notes.map((n) => n.pitch);
  const lo = low ?? (pitches.length ? Math.min(...pitches) - 1 : 59);
  const hi = high ?? (pitches.length ? Math.max(...pitches) + 1 : 73);
  const left = 44;
  const bottom = 22 + (bands.length ? 18 : 0);
  const plotH = height - bottom - 6;
  const rowH = plotH / (hi - lo + 1);
  const x = (t) => left + ((t - from) / (end - from)) * (width - left - 6);
  const y = (p) => 6 + (hi - p) * rowH;

  const text = cssVar("--md-default-fg-color--light", "#666");
  const grid = cssVar("--md-default-fg-color--lightest", "#ddd");
  ctx.font = "11px system-ui, sans-serif";

  // Black-key rows shaded, octave labels on C.
  for (let p = lo; p <= hi; p++) {
    if (isBlackKey(p)) {
      ctx.fillStyle = grid;
      ctx.globalAlpha = 0.35;
      ctx.fillRect(left, y(p), width - left - 6, rowH);
      ctx.globalAlpha = 1;
    }
    if (rowH >= 9 || p % 12 === 0) {
      ctx.fillStyle = text;
      ctx.textBaseline = "middle";
      ctx.fillText(pitchName(p), 2, y(p) + rowH / 2);
    }
  }

  // Time grid.
  ctx.strokeStyle = grid;
  ctx.fillStyle = text;
  ctx.textBaseline = "top";
  const first = Math.ceil(from / timeStep) * timeStep;
  for (let t = first; t <= end + 1e-9; t += timeStep) {
    ctx.beginPath();
    ctx.moveTo(x(t), 6);
    ctx.lineTo(x(t), 6 + plotH);
    ctx.stroke();
    const label = timeLabel(Math.round(t * 1000) / 1000);
    const labelX = Math.min(x(t) + 2, width - ctx.measureText(label).width - 2);
    ctx.fillText(label, labelX, height - bottom + 4);
  }

  // Notes.
  for (const n of notes) {
    if (n.end < from || n.start > end || n.pitch < lo || n.pitch > hi) continue;
    ctx.fillStyle = color(n);
    ctx.globalAlpha = alpha(n);
    const x0 = Math.max(x(n.start), left);
    const w = Math.max(1.5, x(Math.min(n.end, end)) - x0 - 0.5);
    ctx.fillRect(x0, y(n.pitch) + 0.5, w, Math.max(1.5, rowH - 1));
  }
  ctx.globalAlpha = 1;

  // Bands (pedals) below the time axis labels.
  for (const b of bands) {
    if (b.end < from || b.start > end) continue;
    ctx.fillStyle = b.color;
    ctx.globalAlpha = 0.6;
    const x0 = Math.max(x(b.start), left);
    ctx.fillRect(x0, height - 16 + b.row * 8, Math.max(1, x(Math.min(b.end, end)) - x0), 6);
  }
  ctx.globalAlpha = 1;

  if (playhead !== null && playhead >= from && playhead <= end) {
    ctx.strokeStyle = cssVar("--md-accent-fg-color", "#e91e63");
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x(playhead), 6);
    ctx.lineTo(x(playhead), 6 + plotH);
    ctx.stroke();
    ctx.lineWidth = 1;
  }
}
