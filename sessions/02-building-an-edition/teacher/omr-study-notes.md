# OMR insert — evidence and instructor preparation

Added 24 October 2026. Student reference: [From a scan to notation](omr.md).
These notes retain the surviving CAMAT study evidence and current primary
project references. The new Schumann runs below are separate experiments,
prepared on 24 October; they do not reconstruct the deleted Webern outputs.

## What the surviving local study establishes

Read on 24 October 2026:

- [Study README](/home/egor/Nextcloud/code/public_repos/camat_v2/pdf-workflow-test/README.md):
  the folder was reduced on 21 October; OMR runtimes, raw/derived recognition
  outputs, the comparison notebook, study scripts and research snapshots were
  deleted. The old `research/OMR_LINUX_REVIEW.md` link no longer resolves.
- [Handoff, State](/home/egor/Nextcloud/code/public_repos/camat_v2/pdf-workflow-test/HANDOFF.md:8):
  names `webern_omr_comparison.ipynb` as HOMR/OeMeR/Clarity, with SMT++ awaiting
  a checkpoint. This establishes the comparison's recorded scope, not surviving
  error scores or a current performance ranking.
- [Workflow plan](/home/egor/Nextcloud/code/public_repos/camat_v2/pdf-workflow-test/WORKFLOW_PLAN.md:9):
  records HOMR **0.7.0**, 15 recognised measures against 18 printed measures
  on Webern Op. 27/I, PDF p. 1 / printed p. 3. It also records a structural
  workaround needed for symbolic import. Importing the repaired draft did
  not establish musical correctness or recover the missing bars.
- [Workflow plan, OMR pilot](/home/egor/Nextcloud/code/public_repos/camat_v2/pdf-workflow-test/WORKFLOW_PLAN.md:37):
  distinguishes executed HOMR from proposed Audiveris and research adapters
  for SMT++/Zeus. Its older “next comparisons” language and the later handoff's
  comparison description should not be flattened into claims that every tool
  completed the same benchmark.

The 15/18 observation is useful as a classroom failure case. Do not turn it
into note-recognition accuracy, a multi-page aggregate, a Schumann result or
evidence that current HOMR is worse/better than another tool.

## Current references and interfaces checked

- [HOMR README](https://github.com/liebharc/homr/blob/main/README.md), blob
  `99054115b7b4142f17595b47477ae99944c12c6e`.
- [OeMeR README](https://github.com/BreezeWhite/oemer/blob/main/README.md), blob
  `ecc6e9b9e35e13a1cd535c717e7401ac7e1b54cb`.
- [Clarity-OMR README](https://github.com/clquwu/Clarity-OMR/blob/main/README.md), blob
  `6ebaf36fdd81844556306728658584a0017f029d`.
- [SMT README](https://github.com/antoniorv6/SMT/blob/master/README.md), blob
  `9f547a40421ad1207471c61a5ebe222be58ed501`; the old SMT++ repository has an
  explicit migration notice pointing here. Current model input granularity
  and output tokens must be checked for the selected checkpoint.
- [Zeus README](https://github.com/OmniOMR/zeus/blob/main/README.md), blob
  `1c60dad727e92a2afbb125c4d5bdb1025168819f`; the original OLiMPiC repository
  links this refactored package. It documents Python 3.10 and a `predict` CLI
  that writes MusicXML from staff images.
- [Audiveris CLI](https://audiveris.github.io/audiveris/_pages/guides/advanced/cli/):
  `-batch`, `-transcribe`, `-export`, `-save` and `-output` are documented.
- [Edirom DOMD README](https://github.com/Edirom/measure-detector), blob
  `8de5c63ce2123e33617dd1b002f5f91cd1af78b1`: image regions exported as MEI
  measure annotations, separately from musical note transcription.

Project documentation describes intended capabilities, not measured results
on our source. In particular, the HOMR README's limitations and its more
ambitious architecture description are not equivalent to a tested guarantee
that all expressive markings reach the exported file.

## Fresh Schumann recordings — prepared 24 October

Use the [executed reference notebook](references/omr-schumann/02_schumann_omr_recorded.ipynb)
for presentation and the [portable notebook](../notebooks/02_schumann_omr.ipynb)
for code and offline review. [Recorded files](references/omr-schumann/README.md)
include raw exports, conversions/reports, previews, exact environments, model
hashes, source geometry and logs. Source scans and weights stay outside git.

- HOMR 0.7.0, CPU, whole page: completes in about 21 s including first-run
  downloads; 21 measure containers, two staves, no dynamics or words. CAMAT /
  Verovio 6.3.0 import fails with a native segmentation fault. A diagnostic
  prefix of nine measures imports; adding label 10 crashes. The raw file has
  pitched chord members following rests in labels 10–13 and 16–19. No structural
  repair was silently substituted for this raw export. In label 3 the bass F4
  at onset 1 is exported as a member of the upper-staff chord (the crop run reads
  it correctly), so the lower staff sums to 3.5 quarters.
- HOMR 0.7.0, CPU, first-two-system crop: about 9.5 s, nine containers;
  converts and renders with slur warnings. Selected concrete findings are
  documented in the notebook. Its pitches and rhythms match the print in all
  nine containers, both staves (checked 2026-10-26 against the corrected
  starter). It exports no beams, words or dynamics. Its slurs sit on the right
  bass notes, except that the label 4–5 slur has no start. Verovio 6.3 keeps
  the right start and end notes (its MEI slurs have no `@staff`) but draws the
  label 3, 7 and 8 slurs from the upper staff; its import pairs the unmatched
  label-5 stop wrongly and drops the slur that ends in label 6. So most visible
  slur errors are the renderer's, not HOMR's.
- OeMeR 0.1.8, default installation: fails before recognition export with ONNX
  Runtime GPU 1.31.0 (negative-padding model-load error; unavailable CUDA).
  A 1.16.3 CPU attempt also fails to load on this host. Logs are preserved.
- OeMeR 0.1.8 with CPU ONNX Runtime 1.20.1 / NumPy 1.26.4 and the recorded
  compatible dependencies: completes in about 184 s. Its export converts and
  renders, but has 19 containers with label 12 repeated and loses the bass C3
  pickup. No dynamics/slurs are exported. This CPU dependency substitution
  is a local workaround rather than an upstream-supported environment guarantee.

Both full-page runs use the same PNG: original PDF p.8 / printed p.8, 300 dpi,
4167×5617. The crop is (100,500,4000,2280), without resampling. Engine-internal
preprocessing is additional. Timing includes any downloads and is not a speed
ranking. Different scopes, models and setup history prevent that interpretation.

The comparison exposed two errors missed in our preliminary check of the reused
MEI: `d1e338` and `d1e1495` read A3 but the print has F3. Teaching derivatives,
answer key, change record and previews now reflect the print. The technical
baseline and frozen upstream file retain A3. The reference is not a complete
note-level gold standard. No complete correction-time experiment was performed.

All code is retained in `tools/notebooks/02_schumann_omr.py`, with helpers in
`tools/notebooks/helpers/omr.py`. Collection and portable packaging are in
`tools/collect_schumann_omr.py` and `tools/pack_schumann_omr.py`. Optional notebook
cells fetch/check/render the PDF, build isolated Python 3.11 environments from
complete version lists, run both tools, preserve raw exports and invoke CAMAT.

The core workshop continues with the prepared Schumann starter. Remaining
preparation is source-based review/correction of the musical encoding, followed
by facsimile integration and the editing/publishing rehearsal. Live inference
and package/model downloads are unnecessary during the ten-minute insert.
