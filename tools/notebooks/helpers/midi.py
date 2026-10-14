# Read a MIDI file: notes and controllers per track, times in seconds.
# Same rules as the web page's reader: a note-on is paired with the next
# note-off of the same key and channel; notes still open end with the track.

import bisect
import io
import math
import urllib.request

import mido
import numpy as np


def _tempo_map(tempos, ticks_per_beat):
    ticks, seconds, rates = [0], [0.0], [0.5 / ticks_per_beat]  # 120 bpm until the first tempo
    for tick, microseconds in sorted(tempos, key=lambda t: t[0]):
        at = seconds[-1] + (tick - ticks[-1]) * rates[-1]
        rate = microseconds / 1e6 / ticks_per_beat
        if tick == ticks[-1]:
            seconds[-1], rates[-1] = at, rate
        else:
            ticks.append(tick)
            seconds.append(at)
            rates.append(rate)

    def to_seconds(tick):
        i = bisect.bisect_right(ticks, tick) - 1
        return seconds[i] + (tick - ticks[i]) * rates[i]

    return to_seconds


def read_midi(data):
    mid = mido.MidiFile(file=io.BytesIO(data))
    tempos = []
    raw = []
    for track in mid.tracks:
        tick = 0
        events = []
        for msg in track:
            tick += msg.time
            if msg.type == "set_tempo":
                tempos.append((tick, msg.tempo))
            elif msg.type in ("note_on", "note_off", "control_change"):
                events.append((tick, msg))
        raw.append((events, tick))
    to_seconds = _tempo_map(tempos, mid.ticks_per_beat)
    tracks = []
    for index, (events, end_tick) in enumerate(raw):
        open_notes = {}
        notes = []
        controls = []
        for tick, msg in events:
            if msg.type == "control_change":
                controls.append({"control": msg.control, "value": msg.value, "time": to_seconds(tick)})
                continue
            key = (msg.channel, msg.note)
            if msg.type == "note_on" and msg.velocity > 0:
                open_notes.setdefault(key, []).append((tick, msg.velocity))
            elif open_notes.get(key):
                on, velocity = open_notes[key].pop(0)
                notes.append({"pitch": msg.note, "velocity": velocity, "start": to_seconds(on), "end": to_seconds(tick)})
        for (channel, pitch), waiting in open_notes.items():
            for on, velocity in waiting:
                notes.append({"pitch": pitch, "velocity": velocity, "start": to_seconds(on), "end": to_seconds(end_tick)})
        notes.sort(key=lambda n: (n["start"], n["pitch"]))
        tracks.append({"index": index, "notes": notes, "controls": controls})
    return {"tracks": tracks, "duration": max(to_seconds(end) for _, end in raw)}


def load_midi(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return read_midi(response.read())


# What each track of a SUPRA Welte-Mignon file holds: track -> (label, colour number).
ROLES = {
    "raw": {1: ("bass holes", 0), 2: ("treble holes", 1), 3: ("bass expression holes", 2), 4: ("treble expression holes", 3)},
    "exp": {1: ("bass notes", 0), 2: ("treble notes", 1)},
}


# All notes of one version, with the track number as colour and, in the expressive
# file, loudness as opacity: the softest note in the file is pale, the loudest solid.
def roll_notes(midi, version):
    notes = []
    for track in midi["tracks"]:
        if track["index"] not in ROLES[version]:
            continue
        label, colour = ROLES[version][track["index"]]
        for n in track["notes"]:
            notes.append({**n, "track": colour, "role": label, "alpha": 0.9})
    if version == "exp" and notes:
        soft = min(n["velocity"] for n in notes)
        loud = max(n["velocity"] for n in notes)
        for n in notes:
            n["alpha"] = 0.3 + 0.7 * (n["velocity"] - soft) / max(1, loud - soft)
    return sorted(notes, key=lambda n: n["start"])


# Pedal down (controller value >= 64) to pedal up, as bands under the roll.
def pedal_bands(midi):
    track = next((t for t in midi["tracks"] if any(c["control"] == 64 for c in t["controls"])), None)
    bands = []
    if track is None:
        return bands
    for control, row, color, label in [(64, 0, "#2ca02c", "sustain pedal"), (67, 1, "#8c564b", "soft pedal")]:
        down = None
        for c in track["controls"]:
            if c["control"] != control:
                continue
            if c["value"] >= 64 and down is None:
                down = c["time"]
            if c["value"] < 64 and down is not None:
                bands.append({"start": down, "end": c["time"], "row": row, "color": color, "label": label})
                down = None
    return bands


# A very plain synthesiser: enough to hear rhythm, chords and dynamics, not a piano.
# speed: 0.5 plays the window at half speed (twice as long), 2 at double speed.
def synth(notes, start, length, rate=22050, dynamics=True, speed=1.0):
    out = np.zeros(int(rate * (length / speed + 1)))
    for n in notes:
        if not (start <= n["start"] < start + length and 21 <= n["pitch"] <= 108):
            continue
        dur = max(0.02, (min(n["end"], start + length) - n["start"]) / speed)
        level = 0.04 + 0.2 * max(0, n["velocity"] - 20) / 60 if dynamics else 0.12
        k0 = int((n["start"] - start) / speed * rate)
        k1 = min(len(out), k0 + int((dur + 0.4) * rate))
        t = np.arange(k1 - k0) / rate
        freq = 440 * 2 ** ((n["pitch"] - 69) / 12)
        wave = 2 / math.pi * np.arcsin(np.sin(2 * math.pi * freq * t))  # triangle wave
        env = level * (0.3 + 0.7 * np.exp(-np.maximum(t - 0.01, 0) / 0.4))
        env *= np.minimum(1, t / 0.005)
        env[t > dur] *= np.exp(-(t[t > dur] - dur) / 0.05)
        out[k0:k1] += wave * env
    return out
