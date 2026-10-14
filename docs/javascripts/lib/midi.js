// Minimal Standard MIDI File reader: notes with start/end in seconds,
// controllers and text events. Enough for the SUPRA piano-roll files.

function readVarLen(view, pos) {
  let value = 0;
  let byte;
  do {
    byte = view.getUint8(pos++);
    value = (value << 7) | (byte & 0x7f);
  } while (byte & 0x80);
  return [value, pos];
}

function readString(view, pos, length) {
  let s = "";
  for (let i = 0; i < length; i++) s += String.fromCharCode(view.getUint8(pos + i));
  return s;
}

// Tempo map: list of {tick, seconds, secPerTick} segments.
function tempoMap(tempos, ticksPerBeat) {
  const sorted = [...tempos].sort((a, b) => a.tick - b.tick);
  const map = [{ tick: 0, seconds: 0, secPerTick: 0.5 / ticksPerBeat }];
  for (const t of sorted) {
    const last = map[map.length - 1];
    const seconds = last.seconds + (t.tick - last.tick) * last.secPerTick;
    const segment = { tick: t.tick, seconds, secPerTick: t.microseconds / 1e6 / ticksPerBeat };
    if (t.tick === last.tick) map[map.length - 1] = segment;
    else map.push(segment);
  }
  return (tick) => {
    let lo = 0;
    let hi = map.length - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (map[mid].tick <= tick) lo = mid;
      else hi = mid - 1;
    }
    const seg = map[lo];
    return seg.seconds + (tick - seg.tick) * seg.secPerTick;
  };
}

export function parseMidi(buffer) {
  const view = new DataView(buffer);
  if (readString(view, 0, 4) !== "MThd") throw new Error("Not a MIDI file");
  const format = view.getUint16(8);
  const trackCount = view.getUint16(10);
  const ticksPerBeat = view.getUint16(12);
  if (ticksPerBeat & 0x8000) throw new Error("SMPTE time division is not supported");

  let pos = 8 + view.getUint32(4);
  const rawTracks = [];
  const tempos = [];
  const texts = [];
  for (let t = 0; t < trackCount; t++) {
    if (readString(view, pos, 4) !== "MTrk") throw new Error(`Track ${t}: missing MTrk`);
    const end = pos + 8 + view.getUint32(pos + 4);
    pos += 8;
    let tick = 0;
    let status = 0;
    const events = [];
    while (pos < end) {
      let delta;
      [delta, pos] = readVarLen(view, pos);
      tick += delta;
      let byte = view.getUint8(pos);
      if (byte === 0xff) {
        const type = view.getUint8(pos + 1);
        let length;
        [length, pos] = readVarLen(view, pos + 2);
        if (type === 0x51) {
          const us = (view.getUint8(pos) << 16) | (view.getUint8(pos + 1) << 8) | view.getUint8(pos + 2);
          tempos.push({ tick, microseconds: us });
        } else if (type >= 0x01 && type <= 0x07) {
          texts.push({ track: t, tick, text: readString(view, pos, length) });
        }
        pos += length;
        continue;
      }
      if (byte === 0xf0 || byte === 0xf7) {
        let length;
        [length, pos] = readVarLen(view, pos + 1);
        pos += length;
        continue;
      }
      if (byte & 0x80) {
        status = byte;
        pos++;
      }
      const kind = status & 0xf0;
      const channel = status & 0x0f;
      const a = view.getUint8(pos);
      if (kind === 0xc0 || kind === 0xd0) {
        pos += 1;
        continue;
      }
      const b = view.getUint8(pos + 1);
      pos += 2;
      if (kind === 0x90 || kind === 0x80) {
        events.push({ tick, on: kind === 0x90 && b > 0, channel, pitch: a, velocity: b });
      } else if (kind === 0xb0) {
        events.push({ tick, control: a, value: b, channel });
      }
    }
    pos = end;
    rawTracks.push({ events, endTick: tick });
  }

  const toSeconds = tempoMap(tempos, ticksPerBeat);
  const tracks = rawTracks.map((raw, index) => {
    const open = new Map();
    const notes = [];
    const controls = [];
    for (const e of raw.events) {
      if ("control" in e) {
        controls.push({ control: e.control, value: e.value, time: toSeconds(e.tick) });
        continue;
      }
      const key = e.channel * 128 + e.pitch;
      if (e.on) {
        if (!open.has(key)) open.set(key, []);
        open.get(key).push(e);
      } else if (open.get(key)?.length) {
        const start = open.get(key).shift();
        notes.push({
          pitch: e.pitch,
          velocity: start.velocity,
          channel: e.channel,
          start: toSeconds(start.tick),
          end: toSeconds(e.tick),
        });
      }
    }
    for (const queue of open.values()) {
      for (const start of queue) {
        notes.push({
          pitch: start.pitch,
          velocity: start.velocity,
          channel: start.channel,
          start: toSeconds(start.tick),
          end: toSeconds(raw.endTick),
        });
      }
    }
    notes.sort((x, y) => x.start - y.start || x.pitch - y.pitch);
    return { index, notes, controls };
  });

  const duration = Math.max(...rawTracks.map((r) => toSeconds(r.endTick)));
  return { format, ticksPerBeat, tracks, texts, duration };
}
