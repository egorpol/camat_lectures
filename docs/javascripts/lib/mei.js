// Read pitches, metre and key from the MEI that Verovio writes.
//
// Why not Verovio's own MIDI values? Verovio 6.3 drops gestural accidentals
// when it imports **kern: with *k[f#c#], the token 4f# becomes
// <note pname="f"/> and getMIDIValuesForElement() reports F natural.
// So we apply the key signature ourselves:
//   accid.ges > accid > accidental earlier in the bar > key signature.

const STEPS = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 };
const ACCID = { s: 1, f: -1, ss: 2, x: 2, ff: -2, n: 0, xs: 3, ts: 3, tf: -3 };
const SHARP_ORDER = "fcgdaeb";
const FLAT_ORDER = "beadgcf";

export function attrs(text) {
  const out = {};
  for (const m of text.matchAll(/([\w.:]+)="([^"]*)"/g)) out[m[1]] = m[2];
  return out;
}

function keyFromSig(sig) {
  // "2s" -> {f: 1, c: 1}; "0" -> {}
  const m = /^(\d+)([sf]?)$/.exec(sig || "");
  const key = {};
  if (!m) return key;
  const n = +m[1];
  const order = m[2] === "f" ? FLAT_ORDER : SHARP_ORDER;
  for (let i = 0; i < n; i++) key[order[i]] = m[2] === "f" ? -1 : 1;
  return key;
}

// Map xml:id -> MIDI pitch for every <note> with pname and oct.
export function pitchesFromMEI(mei) {
  const pitches = new Map();
  let key = {};
  let carried = new Map(); // "staff:pname:oct" -> alteration, reset per measure
  let staff = "1";
  let note = null; // open <note> waiting for a child <accid>

  const finish = (n) => {
    const where = `${staff}:${n.pname}:${n.oct}`;
    let alter;
    if (n.ges !== undefined) alter = n.ges;
    else if (n.written !== undefined) alter = n.written;
    else if (carried.has(where)) alter = carried.get(where);
    else alter = key[n.pname] || 0;
    if (n.written !== undefined) carried.set(where, n.written);
    pitches.set(n.id, 12 * (+n.oct + 1) + STEPS[n.pname] + alter);
  };

  for (const m of mei.matchAll(/<(\/?)([\w]+)\b([^>]*?)(\/?)>/g)) {
    const [, closing, tag, body, selfClosing] = m;
    if (closing) {
      if (tag === "note" && note) {
        finish(note);
        note = null;
      }
      continue;
    }
    const a = attrs(body);
    if (a.keysig !== undefined) key = keyFromSig(a.keysig);
    if (tag === "keySig" && a.sig !== undefined) key = keyFromSig(a.sig);
    if (tag === "measure") carried = new Map();
    if (tag === "staff" && a.n) staff = a.n;
    if (tag === "note" && a.pname && a.oct !== undefined) {
      const n = {
        id: a["xml:id"],
        pname: a.pname,
        oct: a.oct,
        ges: a["accid.ges"] !== undefined ? ACCID[a["accid.ges"]] : undefined,
        written: a.accid !== undefined ? ACCID[a.accid] : undefined,
      };
      if (selfClosing) finish(n);
      else note = n;
    }
    if (tag === "accid" && note) {
      if (a["accid.ges"] !== undefined) note.ges = ACCID[a["accid.ges"]];
      if (a.accid !== undefined) note.written = ACCID[a.accid];
    }
  }
  return pitches;
}

// Metre {count, unit}; 4/4 if the MEI has none.
export function meterFromMEI(mei) {
  const tag = mei.match(/<meterSig\b[^>]*>/);
  const source = tag ? tag[0] : mei;
  const count = source.match(/\b(?:meter\.)?count="(\d+)"/);
  const unit = source.match(/\b(?:meter\.)?unit="(\d+)"/);
  return count && unit ? { count: +count[1], unit: +unit[1] } : { count: 4, unit: 4 };
}

// First key signature as fifths: 2 = two sharps, -3 = three flats.
export function fifthsFromMEI(mei) {
  const m = mei.match(/\bkeysig="(\d+)([sf]?)"/) || mei.match(/<keySig\b[^>]*\bsig="(\d+)([sf]?)"/);
  if (!m) return 0;
  return m[2] === "f" ? -m[1] : +m[1];
}
