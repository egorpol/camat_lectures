# Live editing: three small changes, then review

Block 2, **0–40 minutes**. Continue with the project from
[facsimile linking](facsimile-linking.md), using
[02_live_editing.ipynb](../../02-building-an-edition/notebooks/02_live_editing.ipynb). The dated
[free-model research](../teacher/vscode-free-models.md) is the preparation handout; account
creation and model downloads belong before class. All tasks also work manually.

## 0–10: open the same file in editor and viewer

1. Open the project in VS Code, with its Python/Jupyter support and the CAMAT
   kernel. Set `PROJECT` in the notebook to the existing `schumann_edition_work`.
2. Confirm the printed absolute path ends in **`edition/mei/work.mei`**. Open
   that exact file beside the notebook. Preserve `linked-starter.mei` and
   `edition/checkpoints/linked-before-editing.mei` as unedited baselines.
3. Run the viewer cell with `auto_watch_mei=True`. Select pickup C3 `d1e60`,
   identify its measure/source zone, then find its ID in the XML.
4. Save the first manual change below; confirm both the **Reloaded** status
   and the visible new marking. Keep source and score navigation aligned.

The viewer is read-only. A local kernel watches a local path; a remote kernel
watches its own filesystem. On Jupyter4NFDI, edit the same file in JupyterLab
unless VS Code is deliberately connected to that remote environment. For a
local file the toolbar says **Reload score**; an HTTP source says **Reload source**.
If events are unreliable, use reload or `auto_watch_mode="always"`. Restart the
kernel/relaunch if widget output stops working; turn off watching at the end.

## 10–18: introduce SVG through three visible changes

Use the [beginner guide](svg-introduction.md) and
[browser demos](../../02-building-an-edition/examples/svg-introduction/index.html) or
[introductory notebook](../../02-building-an-edition/notebooks/02_what_is_svg.ipynb). Change a circle's short
text, enlarge the same drawing as PNG/SVG, and connect Schumann's pickup with
its MEI/SVG address. Highlighting changes appearance; the artificial C3 → F3
example changes musical information and its prepared engraving. Keep path
coordinates, glyphs and CSS optional. The demos run without a model or project.

Then use the [SVG workflow note](svg-editorial-workflow.md) and
[packet notebook](../../02-building-an-edition/notebooks/02_svg_editorial.ipynb) for the actual editing task.
The packet supplies a first-system source crop, current engraving, SVG source
and read-only MEI context. The Webern example and enriched metadata remain
optional extensions once the basic connection is clear.

## 18–23: restore the opening marks manually

Read the first system in full, because the tempo extends beyond the pickup
region. In pickup measure `d1e9` (MEI label 1), add the notebook's `f` and
`Frisch und munter.` fragments **after the staff children**, as measure-level
control events. Save, inspect the diff, and compare source and rendering.
Do not alter note durations to move a mark.

## 23–32: a source-aware model task

Use the packet's prompt to inspect the two opening slur phrases, identify their
MEI endpoints and propose a small candidate edit. The model receives the print,
current engraving and MEI context; SVG source supplies the visual-to-code link.
Do not give it the answer-key endpoints in this task. The candidate workflow
allows local edits, validation and re-rendering while preserving `work.mei`.
Use [svg-candidate-loop.md](../../02-building-an-edition/examples/model-prompts/svg-candidate-loop.md) for
the optional tool-enabled phase after discussing observations.

For A/B, keep the same model and common starting input: A has PNGs + MEI, B adds
SVG text. Optional C replaces it with enriched SVG; this adds explicit encoded
hints and is not a blind perception test. Use a fresh packet after manual edits,
then hold it fixed for all conditions. Record actual SVG transport and human
corrections in the packet's template. See the research note for the protocol.

### Text-only fallback or separate model comparison

Use the notebook's generated prompt or
[restore-forte.md](../../02-building-an-edition/examples/model-prompts/restore-forte.md) with the actual
measure attached. Target **d1e1231 / label 6 / musical bar 5**, the first bar
of the second printed system. It needs a printed forte at its start. Students
first verify this reading against the scan, then ask for one XML insertion.

If comparing models, pairs send the **same prompt/excerpt from the unedited
checkpoint**, in fresh conversations, before either patch is applied. Choose
two named endpoints from the research handout, or label Auto as unknown.
Hold the source description constant: this compares XML assistance, not music
recognition. Optional later extension: provide the same crop to two documented
vision-capable models and separately evaluate the reading they infer.

Read both responses, apply only the accepted insertion, save, then check the
viewer and validator. Keep response text and the final patch separately.
Use [experiment-template.json](../../02-building-an-edition/examples/model-prompts/experiment-template.json)
for model/extension versions, input hash, elapsed time, quota and human decision.
An account/limit failure is a recorded outcome; continue manually.

## 32–40: check the two slurs and explain the decision

Use the exact note IDs in the [teacher key](../../02-building-an-edition/teacher/schumann/answer-key.md):
pickup C3 `d1e60` → F3 `d1e338`, then B-flat3 `d1e561` → A3 `d1e634` as a
separate phrase in label 3. Put each slur in the measure where it starts.
Check endpoints in the rendering against the full printed system.

Add an anchored `<annot>` naming the witness, page, two phrases, inherited
discrepancy and incomplete scope. The optional
[annotation prompt](../../02-building-an-edition/examples/model-prompts/annotate-slurs.md) asks for prose and
anchors without changing music. Review the wording as carefully as the XML.
The starter already corrects the two inherited A3 readings to F3; preserve them.

The minimum outcome is a manual restoration, correct slur endpoints and a
source-based explanation. The representation comparison is optional within
the same time; an instructor demonstration can carry the SVG task. The text-only
forte task remains usable if image access or the live model is unavailable.

## Checks and a recoverable checkpoint

Run the notebook's structural guard and validation, inspect the changed bars
against the scan, and save the experiment record. Schema/reference/resource
and rendering results are distinct; the CAMAT parse consumer is optional and
not requested here. Rhythm advisories inherited outside the edited passage
remain documented. A render alone does not establish source fidelity.

The guard protects existing content/IDs/links and permits new measure-level
dynamic/tempo/slur/annotation elements. It does not verify source readings or
the correctness of the new attributes. Do not rerun integration on the work
file or export a fresh MEI from the renderer. Save a separate checkpoint after
review, keeping its relative graphic paths or the full project together.

The local rehearsal is documented in [teacher/live-editing/checks.json](../../02-building-an-edition/teacher/live-editing/checks.json)
and the [executed reference](../../02-building-an-edition/teacher/references/02_live_editing_recorded.ipynb).
It uses deterministic teacher fragments, not responses from the researched
models. Browser/frontend behavior and student provider accounts remain separate
classroom checks. The next outline segment is the mei-friend alternative.
