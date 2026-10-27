# Recorded local editing rehearsal

Executed **25 October 2026** with the fresh PyPI CAMAT 0.2.8 environment used
for PDF preparation. See [environment.json](environment.json),
[checks](../../live-editing/checks.json) and
[executed notebook](../02_live_editing_recorded.ipynb).

The first part runs the student notebook against an isolated copy of the linked
project. Extra, explicitly labelled instructor cells then insert the **six
prepared teacher fragments**: opening dynamic/tempo, second-system forte, two
slurs and one annotation. These are deterministic fixtures, not output from any
researched model. No provider account, key or inference request was used.

Both normal file writes and atomic replacements caused completed native
watch-triggered re-renders (revisions 1 → 2 → 3). The rebuilt widget HTML contains
the new dynamic/slur IDs and annotation label. This checks the kernel, observer
and rebuilt widget content. It does **not** verify VS Code's frontend scroll/
selection retention or constitute a new browser interaction test.

[edited-example.mei](edited-example.mei) passes the recorded
[validation](validation/run.json): required MEI 5.1/reference/resource checks,
plus Verovio rendering. The optional CAMAT parse consumer was not requested;
its diagnostic coverage remains incomplete. Inherited rhythm advisories remain
in [findings](validation/findings.json). The guard separately rejected modified
pitch, image path and existing header data. The original project working file
was checked byte-for-byte and preserved. No human source approval is asserted.

No scan pixels, viewer HTML or saved widget state are included in this reference.
The MEI retains its runtime `../pages/page-0001.png` graphic path. Recreate the
project with the preceding notebooks and place a copy under `edition/mei/` to
resolve it; this reference folder alone is not a complete image bundle.
The existing provenance/header and [license notice](LICENSE) are retained.

Reproduce in a new scratch folder from the repository root, using the CAMAT
notebook environment:

```sh
python tools/rehearse_schumann_editing.py \
  --project /absolute/path/to/schumann_edition_work \
  --output /tmp/schumann-editing-new
```

The output directory must not already exist. The script copies only `edition/`,
does not rerun linking, and strips image-bearing output/widget state from the
recorded notebook. The ordinary student notebook never applies these fixtures.
