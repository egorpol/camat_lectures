# From a scan to notation: where OMR fits

Session 2 reference sheet. Project documentation checked **24 October 2026**.
The earlier CAMAT Webern study supplies a practical case; these references do
not constitute a new comparison of current model accuracy.

## The shared preparation and the two image-based tasks

First identify the PDF witness, preserve its bytes, choose the pages and render
them to images. A fixed-resolution **PNG** is convenient for this workshop;
JPEG can also be an OMR input, but lossy compression changes the pixels.
Any crop, rotation or deskewing creates a separately recorded derivative.

The same page image can then support two different tasks:

```text
PDF witness → fixed page image
                   ├─ OMR → draft MusicXML / notation tokens → correction → musical MEI
                   └─ measure detection → bar boxes / sparse MEI ───────────────┐
                                                                             ↓
Existing encoding or manual entry → musical MEI ───────────────→ align and review
                                                                             ↓
                                                         MEI + linked facsimile
```

**OMR (optical music recognition)** attempts to infer notes, durations, voices
and other notation. Its output is an editable draft. The available export
format depends on the tool; MusicXML commonly passes through CAMAT/Verovio
to become the working MEI.

**Measure detection** locates regions on the image. The
[Edirom Deep Optical Measure Detector](https://github.com/Edirom/measure-detector)
can express these annotations as sparse MEI. It supplies page regions and
measure references; the musical notes come from a separate encoding, manual
transcription or an OMR result. Matching the boxes to the musical MEI requires
review even when their counts agree.

Our Schumann route reuses a known musical encoding, then enriches it from the
selected print. This saves recognition and correction work. The base encoding
still needs source comparison: the opening slurs and second-system dynamic
already demonstrate differences from our witness.

## Python projects from the CAMAT comparison

### HOMR

[HOMR repository and usage](https://github.com/liebharc/homr).
The documented workflow accepts score pictures/PDFs and exports MusicXML.
Its current quick start provides a CPU backend as well as GPU options, making
it a practical candidate for an instructor-prepared example. The documentation
lists pitch/rhythm limitations; check expressive detail against the actual
output rather than assuming the export contains every printed sign.

**CAMAT connection:** the surviving study records a **HOMR 0.7.0** pilot on
Webern Op. 27/I, first PDF page / printed p. 3. It produced **15 encoded
measures for 18 printed bars**, so the alignment check stopped. This historical
result concerns one page and one setup. It is not “83% accuracy,” a result on
Schumann, or a measurement of today's HOMR version.

### OeMeR

[OeMeR repository and usage](https://github.com/BreezeWhite/oemer).
A Python image-to-MusicXML pipeline with a diagnostic image of recognised
elements. Its documented default inference backend is ONNX Runtime, with a
TensorFlow option. It is useful for discussing how staff/symbol segmentation
and musical reconstruction interact. First use needs model downloads.

**CAMAT connection:** named alongside HOMR and Clarity in the old comparison
notebook's surviving description. Per-tool outputs and quantitative results
are no longer available in the cleaned study folder, so no numerical ranking
is reconstructed here.

### Clarity-OMR

[Clarity-OMR repository and usage](https://github.com/clquwu/Clarity-OMR).
A Python/PyTorch project whose CLI takes a PDF and exports MusicXML. The
documented pipeline renders pages, detects staff regions, recognises notation
tokens and assembles the score. It exposes PDF DPI and intermediate-work-folder
options, which make the shared image-preparation stage particularly visible.

**CAMAT connection:** named in the same comparison notebook description.
Treat successful inference, a readable export and agreement with the print
as separate checks; the surviving notes do not establish its comparative score.

## Further references

- **Sheet Music Transformer / SMT++:** the historical
  [SMT++ repository](https://github.com/antoniorv6/SMT-plusplus) now points to
  [the main SMT project](https://github.com/antoniorv6/SMT). Its Python/PyTorch
  examples predict notation-token sequences. Select an actual model checkpoint
  for the intended system/page input and inspect the output vocabulary and
  conversion route. In the old CAMAT notes SMT++ was still awaiting a checkpoint;
  it is not counted as a completed local benchmark. Research reference:
  [Ríos-Vila et al., *End-to-End Full-Page Optical Music Recognition for Pianoform Sheet Music*](https://arxiv.org/abs/2405.12105).
- **Zeus:** the original [OLiMPiC study](https://github.com/ufal/olimpic-icdar24)
  now directs users to [OmniOMR/zeus](https://github.com/OmniOMR/zeus), a Python
  package with CLI/API support and MusicXML prediction from staff/grandstaff
  images. Its current documentation specifies Python 3.10; use a separate
  environment/CLI alongside the CAMAT workshop environment. The old CAMAT plan
  listed it as a research-adapter candidate, without a completed comparison.
- **Audiveris:** [the documented batch CLI](https://audiveris.github.io/audiveris/_pages/guides/advanced/cli/)
  exports MusicXML and preserves an editable `.omr` project. It is a Java
  application that Python can call as an external process. It is useful for
  comparing an interactive correction workflow with model-driven Python tools.
  The old study proposed it; its installation/run was not established there.

## Ten-minute seminar insert

1. **Two minutes:** follow the two image-based branches above. Identify what
   each output contains and what still has to be supplied.
2. **Three minutes:** use the [executed Schumann notebook](references/omr-schumann/02_schumann_omr_recorded.ipynb)
   to compare the full-page and cropped HOMR drafts, then OeMeR's export.
   Discuss the failed full-page import and OeMeR's 19 containers with a repeated
   label. The Webern 15-versus-18 result is additional historical context.
3. **Three minutes:** inspect one source bar, the draft and the prepared MEI.
   The comparison caught two A3 → F3 errors in the reused encoding; the print
   governs both input routes. List checks for any draft:
   pitch/octave and accidental, duration/rest, staff/voice assignment, and
   missing expressive marks. Rendering or counting bars alone cannot settle them.
4. **Two minutes:** choose the practical route: hand entry, reusing an encoding,
   or OMR followed by correction. Continue the core exercise with the prepared
   Schumann starter so the rest of the workflow has a stable input.

The [portable Schumann notebook](../notebooks/02_schumann_omr.ipynb) now preserves
real HOMR 0.7.0 and OeMeR 0.1.8 CPU runs, raw MusicXML, converted MEI where
import succeeded, engraved previews, logs, environments and model hashes.
It runs offline in recorded-review mode with `schumann-omr-recordings.zip` beside it; optional cells
prepare the PDF and run fresh inference in separate environments. Source scans
and model weights are fetched at runtime. The prepared MEI is a documented
teaching reduction, with selected source checks, rather than a complete gold
standard. See the [recordings](references/omr-schumann/README.md) for provenance.

For a small comparison, record errors by bar and the time needed to correct
them. Keep wrong/missing bars separate from pitch, duration, voice and expression
errors. Preserve raw recognition and corrected notation as different files.
Use lossless page images for reproducibility and keep their pixel geometry
consistent with the zones used by the facsimile viewer.
