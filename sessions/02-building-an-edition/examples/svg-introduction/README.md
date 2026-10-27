# Local SVG introduction

Open **index.html** in a browser. All scripts, drawings and data are local; no
web server, account or model call is needed. Keep the files together.

Three demos cover a circle described as text, PNG versus vector enlargement,
and the same Schumann pickup note in MEI and Verovio SVG. The SVG source shown
to students is deliberately short. Real glyph paths remain in the SVG assets.

The circle and note-symbol drawing are new teaching graphics. The tiny PNG is
rasterized from `note-symbol.svg`; the pixel-grid display is a deliberate
nearest-neighbour enlargement, with ordinary smoothing available too. It is
not a historical scan. This is a comparison of these two prepared images,
not a general claim that every SVG is compact, contains only vectors or
encodes musical semantics.

`pickup-c3.mei` derives from the existing teaching manual-entry solution,
retains only its pickup, preserves credits and adds a demonstration statement.
`pickup-f3.mei` differs only in the pitch name of `d1e60` (C → F, same octave
and duration). F3 is artificial, not an edition correction. Both were rendered
in advance with Verovio 6.3. The browser changes between prepared renderings;
it does not run a live engraver. The enriched variants repeat pitch/duration
as SVG `data-*` attributes.

Preserve the header and accompanying [license](LICENSE). `manifest.json`
records the input identity, renderer and asset hashes. Source scans are absent.
