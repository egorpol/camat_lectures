# Schumann facsimile exercise — instructor key

Use the [student guide](../../../03-linking-and-editing/guides/facsimile-linking.md). The deliberate omission is
**MEI label 1**, the short pickup at the beginning of the first system.
It is a constructed manual-data exercise rather than an observed detector error.

## Region to add

The prepared solution is `(400, 600, 872, 1360)`, in full-resolution PNG pixels.
This covers the initial clefs, pickup rest/note, forte and both staves. The
opening verbal direction extends into the next bar; the region is not a
segmentation of all symbols belonging semantically to the pickup.

Nearby carefully inspected coordinates are acceptable if they include the
intended music, stay in the image, form the correct system and do not mostly
cover a neighbouring retained box. The next retained region has left/right
856–1600 and the same top/bottom. Slight barline overlap is intentional.

Expected counts before correction: `[4,4,4,4,4]`; after correction:
`[5,4,4,4,4]`. The added region is appended to the raw list by CAMAT but sorted
to its correct musical position during alignment. Raw box indices therefore
must not be mistaken for MEI labels or measure IDs.

## Expected linked result

- One facsimile tied to `#src.imslp51556`, one surface labelled 8, one graphic.
- 21 zones and 21 linked musical measures, labels 1–21.
- One page break and four system breaks, before labels 1, 6, 10, 14 and 18.
- `graphic/@target="../pages/page-0001.png"` from `edition/mei/`.
- Pickup measure `d1e9` points to zone suffix `001`.
- Label 6 (`d1e1231`) points to zone suffix `006`.
- Final label 21 (`d1e5813`) points to zone suffix `021`.
- Existing note/rhythm/voice data and IDs are preserved; `mdiv/@n="1"` is the
  declared normalization needed for the sole unnumbered movement.

The ordinary run leaves review unapproved until the actual reviewer enables
confirmation with their name. The agent's preparation checks do not stand in
for instructor/student approval. The rendered note data remain a teaching
reduction; source-based musical editing follows in Block 2.

`work.mei` is created once beside the generated baseline. A repeat run retains
later edits in that file. The immutable `linked-before-editing.mei` snapshot
and linked baseline provide the comparison stage for the editing exercise.

The viewer may list the inherited, unanchored header copyright annotation.
That is retained provenance rather than a completed editorial task; preserve it.
