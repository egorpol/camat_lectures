# SVG editorial packet: executed local evidence

Prepared and executed **26 October 2026** with PyPI CAMAT 0.2.8 and Verovio
6.3.0. See [checks](../../svg-editorial/checks.json),
[research/teaching note](../../../../03-linking-and-editing/guides/svg-editorial-workflow.md) and
[executed notebook](../02_svg_editorial_recorded.ipynb).

The notebook exports the existing linked first-system MEI as default and
enriched SVG, plus a PNG engraving, source-system crop and read-only MEI context.
It preserves the original input and makes **zero provider calls**. All five
measures, including the pickup, are present; 100 note/chord/rest/control events
map to existing IDs in the SVG. Both variants retain their glyph definitions.
Default and enriched SVG produce pixel-identical PNGs with librsvg; the added
`data-*` values change the available structured information, not the picture.
The CairoSVG fallback is documented but was not exercised in this run.

Files retained here:

- `score.svg` / `score-enriched.svg`: before-editing examples, with existing
  MEI IDs/classes and optional encoded attributes.
- `context.xml`: scoreDef and five measures as a read-only fragment; it is
  deliberately not a valid standalone MEI document. Its facsimile IDs belong
  to the complete project.
- `element-map.json`, `prompt-A.md`, `prompt-B.md`, `prompt-C.md` and
  `record-template.json`: input scaffolding and an unfilled experiment record.
- `manifest.json`: original local packet identity, crop coordinates, tool options
  and hashes. It lists two PNGs intentionally **not included here**: the scan
  crop stays local, and the before engraving is reproducible from the SVG.
- `candidate-two-slurs.mei`, `candidate-enriched.svg` and
  `candidate-engraving.png`: a deterministic teacher fixture that adds just the
  two answer-key slurs, for reviewing the candidate loop. These are not model
  outputs. The extra SVG attributes expose the exact `startid`/`endid` values.
- `validation/`: executed required XML/reference/MEI 5.1/resource checks and
  Verovio rendering, all passing. CAMAT parse was not requested; consumer
  diagnostic coverage remains incomplete. Inherited rhythm advisories remain.

The crop and candidate engraving were inspected by the assistant; this is not
a claim of instructor/student source approval. The original working file was
checked unchanged. Same-input reuse preserved packet files, and the exporter
rejected changed input or modified existing packet files without overwriting.

The recorded notebook omits image-bearing outputs and contains no inline media
payload. None of these SVGs embeds the scan. The candidate MEI retains its
runtime `../pages/page-0001.png` target, so place a copy under the reconstructed
project's `edition/mei/` to resolve it. Preserve the [license](LICENSE) and header.

Recreate a packet from the full project, with Verovio, Pillow and either
`rsvg-convert` or CairoSVG/system Cairo available:

```sh
python tools/export_svg_editorial.py --mei /path/to/edition/mei/work.mei --output /tmp/new-svg-packet
```

The source scan is cropped from the linked local page; nothing is downloaded.
For model tests, use the generated source crop as well as the engraving. The
current SVG/context alone cannot establish which signs the print contains.
