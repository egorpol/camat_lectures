# Prepare the Schumann PDF and describe the page

Session 2, **45–65 minutes**. Run [the student notebook](../notebooks/02_pdf_preparation.ipynb)
with [schumann-edition-inputs.zip](../notebooks/schumann-edition-inputs.zip) beside it.
The [executed reference](references/02_pdf_preparation_recorded.ipynb) preserves
the text checks; source-scan image outputs are cleared from that saved copy.
Both notebook downloaders include the separate ZIP. There is no encoded data
blob in the notebook.

## The twenty-minute route

1. **45–50: freeze the source and identify the derivative.** Inspect the source
   URL and expected hash. Obtain the frozen original volume, then extract the
   relevant leaf. Distinguish original PDF page **8**, excerpt PDF page **1**,
   and printed page **8**. The excerpt's metadata is part of its PDF identity.
2. **50–55: render the excerpt.** CAMAT makes one 300 dpi PNG and `pages.json`.
   Inspect the full page and confirm 4167 × 5617 pixels. The displayed preview
   is smaller; later coordinates refer to the full-resolution PNG.
3. **55–60: resolve the pickup and count systems.** Read the labels from
   `music/body`, preserving labels 1–21. Label 1 is the pickup; label 2 is the
   first full bar. The five systems contain 1–5, 6–9, 10–13, 14–17 and 18–21.
4. **60–65: describe and check.** Enter the page description below. Run the
   two dry-run counterexamples and save the checkpoint. Both partners should
   be able to locate the page and system of any requested MEI label.

```text
1 | 8 | 1-5, 6-9, 10-13, 14-17, 18-21
```

Here `1` names the excerpt PDF page; `8` is the printed page. Commas separate
systems. These are MEI labels, not numbers printed over the bars.

## Rehearse setup before class

Use Python 3.11+ with `camat[validation,notebooks]==0.2.8`, `pypdf==6.10.0`,
and Verovio 6.3.0. Poppler's `pdfinfo` and `pdftoppm` must be available on the
kernel machine. The notebook checks them before beginning. Student cloud
and desktop setups still need a classroom rehearsal.

By default the notebook fetches the frozen IMSLP PDF when it is missing.
For an offline class, put that original in
`schumann_edition_work/sources/imslp-51556-schumann-op68.pdf` beforehand, or set
`LOCAL_ORIGINAL` to its path and disable the download. The 9.4 MB volume is
checked against the recorded SHA-256 before it is used. This stage does not
send any image to an external measure detector.

The 15 KB input ZIP contains only notation, credits, source metadata and
settings. The scan remains a runtime input. The original volume is retained;
the helper recreates the separately identified one-page derivative with the
same title, subject and creator metadata as the frozen preparation copy.

## What to inspect in the outputs

The project contains:

- `inputs/`: a checked copy of the starter, settings, source record and license.
- `sources/`: the unchanged original, one-page derivative and `page-mapping.json`.
- `edition/pages/`: full-resolution PNG, `pages.json` and Poppler's page information.
- `edition/measure-page-map.json`: 21 rows connecting measure IDs/labels to
  systems and all three page-number conventions.
- `page-preparation-checkpoint.json`: the input/image hashes and handoff state.

The notebook rejects a description missing the pickup. It also demonstrates
that moving label 5 into the wrong system can still pass the label coverage
and order check. The image comparison supplies the system-boundary evidence.
The checkpoint verifies the prepared description, input identities, dimensions
and measure IDs; it does not establish musical source fidelity.

Keep the whole project together for the **65–85 minute** measure-box exercise.
The musical MEI remains unchanged at this stage. The following block adds
reviewed zones, then links them to the musical measures. The core editorial
passage remains labels 1–9; the remaining measures are a technical carrier.

## Rehearsal record

The notebook was executed on 25 October 2026 in a **fresh PyPI installation of
CAMAT 0.2.8**, without importing the development checkout. It reproduced the
frozen one-page derivative, rendered the expected page, and saved the full
five-system checkpoint. The rendered PNG matches the full-page input used
in the recorded OMR examples. See [technical evidence](pdf-preparation/checks.json)
and [recorded manifests](references/pdf-preparation/README.md).

The Python source is `tools/notebooks/02_pdf_preparation.py`; preparation
helpers are in `tools/notebooks/helpers/pdf_preparation.py`. The data ZIP is
built by `tools/pack_schumann_pdf_inputs.py`, before rebuilding notebooks.
