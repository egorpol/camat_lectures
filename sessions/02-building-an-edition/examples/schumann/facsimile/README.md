# Manual Schumann measure regions

Prepared 25 October 2026 for the [linking exercise](../../../../03-linking-and-editing/guides/facsimile-linking.md).
Both JSON files identify the fixed 300 dpi PNG (4167×5617) by SHA-256.

- `boxes-checked.json`: 21 prepared rectangles with MEI labels and system numbers.
- `boxes-exercise.json`: deliberately omit label 1, the pickup, leaving 20.

These are AI-assisted manual coordinates, visually inspected as full-page and
five system overlays. No external measure detector was called. Instructor or
student approval must be recorded after their own inspection. The word
“checked” identifies the prepared answer dataset; it does not assert a human
musical proofread.

Coordinates refer to the entire PNG, not a resized notebook screenshot. Rectangles
cover both piano staves, with small barline margins; cross-bar slurs/text can
extend beyond them. Page mapping: original PDF 8 → excerpt PDF 1 → printed 8.
The image and source PDFs are runtime inputs and are excluded here.

`tools/pack_schumann_boxes.py` produces the separate notebook ZIP from these
JSON files. No image or Base64 data is included in the ZIP or notebook source.
