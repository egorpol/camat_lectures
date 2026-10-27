# Schumann OMR recordings — 24 October 2026

Use the [executed reference notebook](02_schumann_omr_recorded.ipynb) to inspect
the results. The portable [student notebook](../../../notebooks/02_schumann_omr.ipynb)
loads these recordings from the separate `schumann-omr-recordings.zip` data file.
Keep the ZIP beside a downloaded notebook for offline review; `get_notebooks.py`
copies both files. There is no encoded data blob in the notebook.
Its optional cells prepare the source and run fresh recognition/conversion.

Two HOMR 0.7.0 CPU examples: whole page and first two systems. OeMeR 0.1.8
records the initial GPU-runtime failure, an older CPU-runtime load failure,
and the CPU 1.20.1 attempt. Read each run.json for its actual outcome.
These are selected case studies, not an accuracy or speed ranking.

Raw MusicXML exports are untouched. converted/ contains CAMAT outputs/reports;
rendered/ contains engravings and exact renderer diagnostics. reference/ holds
the deliberately reduced teaching MEI, its first-nine-measure selection and
the upstream license. The print governs musical decisions. The comparison
found two A3 → F3 discrepancies in the reused MEI; the teaching files now
record those corrections. No complete note-level gold standard is claimed.

run.log is a reading copy with download progress and ANSI colour removed.
run-original.log.gz preserves the exact original; log-provenance.json records
both identities. Original compressed logs are omitted from the portable bundle.
run.json records command, timestamp, elapsed time, package versions, input/output
hashes and model hashes. Timings include first-run downloads where applicable.
requirements.txt freezes each complete environment, installed with --no-deps.
For OeMeR CPU this deliberately substitutes onnxruntime for its declared GPU
dependency; it is a tested local workaround, not a supported platform guarantee.

Source PDFs/images, diagnostic images and models are excluded. Fetch the scan
at runtime; see source.json and source-catalogue.json. Input was original PDF
p.8 / printed p.8 (300 dpi, 4167×5617); the HOMR crop is (100,500,4000,2280),
without resampling. Engine-internal resizing/preprocessing is additional.
The reference notebook does not embed scanned source images.

To reproduce the portable bundle after changing these files:
`python tools/pack_schumann_omr.py`, then `python tools/build_notebooks.py`
(from the repository root). Recording collection is in tools/collect_schumann_omr.py;
the notebook source is tools/notebooks/02_schumann_omr.py and the invocation,
preparation and inspection helpers are tools/notebooks/helpers/omr.py.
