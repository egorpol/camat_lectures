// Facsimile links in MEI: the page image, its zones and the measures that
// point to them with @facs. Also builds IIIF Image API URLs for the page
// and for one zone of it, and cuts each measure out of the file text.

const XML_ID = "xml:id";

// One <surface> per file is enough for the session-1 demo; we take the first.
export function facsimileFromMEI(text) {
  const doc = new DOMParser().parseFromString(text, "application/xml");
  if (doc.querySelector("parsererror")) throw new Error("the MEI file is not well-formed XML");
  const graphic = doc.querySelector("facsimile surface graphic");
  if (!graphic) throw new Error("the MEI file has no <facsimile> with a <graphic>");
  const surface = {
    target: graphic.getAttribute("target"),
    width: Number(graphic.getAttribute("width")),
    height: Number(graphic.getAttribute("height")),
  };
  const zones = new Map();
  for (const z of doc.querySelectorAll("facsimile zone")) {
    const [ulx, uly, lrx, lry] = ["ulx", "uly", "lrx", "lry"].map((a) => Number(z.getAttribute(a)));
    zones.set(z.getAttribute(XML_ID), { id: z.getAttribute(XML_ID), ulx, uly, lrx, lry });
  }
  const measures = [];
  for (const m of doc.querySelectorAll("measure[facs]")) {
    const zone = zones.get(m.getAttribute("facs").replace(/^#/, ""));
    if (!zone) continue;
    const notes = [...m.querySelectorAll('annot[type="editorial"]')].map((a) => ({
      text: a.textContent.trim().replace(/\s+/g, " "),
      targets: (a.getAttribute("plist") || "").split(/\s+/).filter(Boolean).map((r) => r.replace(/^#/, "")),
    }));
    const id = m.getAttribute(XML_ID);
    measures.push({ id, n: m.getAttribute("n"), zone, notes, source: measureSource(text, id) });
  }
  return { surface, measures };
}

// The <measure> element as it is written in the file (not re-serialised),
// with its first and last line numbers. Indentation is kept relative to
// the <measure> tag.
export function measureSource(text, id) {
  const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const start = text.search(new RegExp(`<measure\\b[^>]*\\sxml:id=["']${escaped}["']`));
  if (start < 0) return null;
  const openTag = text.slice(start, text.indexOf(">", start) + 1);
  const end = openTag.endsWith("/>") ? start + openTag.length : text.indexOf("</measure>", start) + "</measure>".length;
  const lineStart = text.lastIndexOf("\n", start) + 1;
  const indent = /^[ \t]*$/.test(text.slice(lineStart, start)) ? text.slice(lineStart, start) : "";
  const lines = text
    .slice(start - indent.length, end)
    .split("\n")
    .map((line) => (line.startsWith(indent) ? line.slice(indent.length) : line));
  const first = text.slice(0, start).split("\n").length;
  return { text: lines.join("\n"), first, last: first + lines.length - 1 };
}

// target is a IIIF Image API URL: {base}/{region}/{size}/{rotation}/{quality}.{format}
export function iiifUrl(target, { region = "full", size = "full" } = {}) {
  const base = target.replace(/\/[^/]+\/[^/]+\/[^/]+\/[^/]+\.(jpg|png|webp)$/, "");
  return `${base}/${region}/${size}/0/default.jpg`;
}

// Zone coordinates are in the graphic's pixel space; IIIF "pct:" regions
// work whatever size the server's full image is.
export function zoneRegion(zone, surface) {
  const pct = (v, total) => ((100 * v) / total).toFixed(3);
  return (
    "pct:" +
    [
      pct(zone.ulx, surface.width),
      pct(zone.uly, surface.height),
      pct(zone.lrx - zone.ulx, surface.width),
      pct(zone.lry - zone.uly, surface.height),
    ].join(",")
  );
}
