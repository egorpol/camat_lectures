// Verovio in the browser: one shared WebAssembly module, loaded on first use.
// We use the build with Humdrum support: the default build cannot read
// **kern or EsAC (tested with 6.3.0). Keep the version in step with the
// notebooks' `pip install verovio==6.3.0`.

import { precheck } from "./checks.js";
import { pitchesFromMEI, meterFromMEI, fifthsFromMEI } from "./mei.js";
import { notesFromTimemap } from "./grid.js";

export const VEROVIO_VERSION = "6.3.0";
const CDN = `https://cdn.jsdelivr.net/npm/verovio@${VEROVIO_VERSION}/dist/`;

let ready = null;

// Verovio 6.3.0's ABC reader keeps a key signature's sharps and flats in the
// module: after a K:G tune, the F of a later K:C tune comes back as F#
// (accid.ges="s"), even in a new toolkit. Only a fresh module forgets them.
let abcKeyLeft = false;

async function createModule() {
  const [{ default: createVerovioModule }, esm] = await Promise.all([
    import(CDN + "verovio-module-hum.mjs"),
    import(CDN + "verovio.mjs"),
  ]);
  const module = await createVerovioModule();
  esm.enableLogToBuffer(true, module);
  esm.enableLog(esm.LOG_WARNING, module);
  return { module, esm };
}

export function verovioReady() {
  ready ??= createModule();
  return ready;
}

// Load text in one format and return what the demos need.
// width: target width in CSS pixels; Verovio lays the music out to fit it.
export async function readScore(format, text, { width = 700, scale = 40, header = "auto", svg = true } = {}) {
  const { errors, warnings } = precheck(format, text);
  const result = { ok: false, errors, warnings, log: "", svg: "", mei: "", timemap: [], notes: [] };
  if (errors.length) return result;
  if (format === "abc" && abcKeyLeft) {
    ready = null;
    abcKeyLeft = false;
  }
  const { module, esm } = await verovioReady();
  let tk = null;
  try {
    tk = new esm.VerovioToolkit(module);
    tk.setOptions({
      inputFrom: format,
      scale,
      pageWidth: Math.max(600, Math.round((width * 100) / scale)),
      adjustPageHeight: true,
      pageMarginTop: 30,
      pageMarginBottom: 30,
      pageMarginLeft: 30,
      pageMarginRight: 30,
      header,
      footer: "none",
    });
    result.ok = Boolean(tk.loadData(text));
    result.log = tk.getLog().trim();
    if (!result.ok) {
      result.errors.push("Verovio could not read this text as " + format + ".");
      return result;
    }
    if (svg) {
      const pages = [];
      for (let p = 1; p <= tk.getPageCount(); p++) pages.push(tk.renderToSVG(p));
      result.svg = pages.join("");
    }
    result.mei = tk.getMEI();
    result.timemap = tk.renderToTimemap({ includeMeasures: true, includeRests: true });
    result.notes = notesFromTimemap(result.timemap, pitchesFromMEI(result.mei));
    result.meter = meterFromMEI(result.mei);
    result.fifths = fifthsFromMEI(result.mei);
    result.log = [result.log, tk.getLog().trim()].filter(Boolean).join("\n");
    return result;
  } catch (error) {
    // Verovio crashed. The module may be damaged: start a fresh one.
    ready = null;
    result.ok = false;
    result.errors.push(
      `Verovio crashed on this text (${error?.message || error}). ` +
        "This happens with some broken input that Verovio does not report as an error. Undo your last change and try again."
    );
    return result;
  } finally {
    if (format === "abc" && (!result.ok || result.fifths)) abcKeyLeft = true;
    try {
      tk?.destroy?.();
    } catch {
      /* the toolkit died with the module */
    }
  }
}
