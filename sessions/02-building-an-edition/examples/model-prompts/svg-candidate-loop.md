# Optional local candidate-editing prompt

Use this after discussing the model's observations from `prompt-B.md` or
`prompt-C.md`. Replace the paths with actual local paths and ensure the
candidate initially matches the packet input hash. This is a bounded tool
exercise; it is not the A/B perception comparison's initial prompt.

---

Work only on the candidate MEI at `<candidate-path>` and new output files in
`<attempt-output-path>`. The source and current engraving/context are in
`<packet-path>`. The canonical working MEI is `<work-path>`; preserve it.

Use only these task inputs. Do not consult teacher answer keys, other editions
or the web. Compare the scan's two opening slur phrases, explain the evidence,
and identify their start/end note IDs. If an endpoint remains ambiguous, report
it without applying that uncertain change.

Apply the smallest supported slur patch to the candidate, using new unique IDs.
Keep notes, durations, voices, existing IDs, metadata, facsimile links and
source breaks unchanged. Edit the MEI, then render from it; keep SVG as a
derived inspection artifact. You may run these local checks/tools:

```sh
python <lecture-repository>/tools/export_svg_editorial.py --mei <candidate-path> --output <attempt-output-path>/render
camat-validate-mei <candidate-path> --output-dir <attempt-output-path>/validation --verovio
```

Inspect the new engraving against the scan. You may make one further targeted
revision, using a new render-output directory. Separate a source-reading issue,
an encoding error and a renderer limitation in your explanation.

Return the exact diff, source evidence, proposed anchors, actual check results,
any remaining uncertainty and which images/files you were able to inspect.
Leave accepting the candidate and recording source approval to the human editor.
