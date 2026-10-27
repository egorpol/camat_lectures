# Schumann source and facsimile instructions

Witness: Clara Schumann edition, Breitkopf & Härtel, plate R.S.67, Leipzig,
catalogued 1887; IMSLP file 51556. Scan credit: D-Mbs / Bayerische Staatsbibliothek.
Catalogue: https://imslp.org/wiki/Special:ImagefromIndex/51556

The viewer expects the single full page containing No.10: original PDF page 8,
excerpt page 1, printed page 8. The complete 50-page PDF does not match this
one-page viewer manifest. Do not crop or rescale the extracted PDF.

Original SHA-256:
893ab03c376724a9f4474497130eb2d8510ba9d71f05bb270c8f6000b731e289
Expected one-page excerpt SHA-256:
3c634e9fa1c8b4f75df6abbd1f2edf9012625421abf2eee37e641e70e794ef8e

From the repository, after installing requirements:
python scripts/prepare_source.py --original /path/to/the-original-imslp-51556.pdf
or explicitly download the recorded original:
python scripts/prepare_source.py --download

Then open local/schumann-op68-no10-source-page.pdf using the viewer's PDF button.
The PDF is read in your browser; this site does not upload it. Page images and
PDF bytes are omitted from the published build and the template ZIP.

The exported local project may already include the exact excerpt and prepared
page image in ignored local/ and pages/ folders. To recreate page images and
check resources from scratch, follow the seminar PDF-preparation notebook with
its frozen renderer settings; the source script above only recovers the PDF.

MEI labels: 1 = pickup, 2 = first full bar. The technical file has 21 measure
elements. Three exercise edits do not constitute a complete edition of every
mark in the first eight full bars or the whole piece. Read review.json for the
actual reviewed scope, person and unresolved issues.
