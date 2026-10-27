# SVG-aware editorial work with an LLM

Research and teaching proposal, **26 October 2026**. This extends the
[live-editing block](live-editing.md): the model can inspect an engraving,
locate a discrepancy, draft a targeted MEI edit and inspect the new rendering.
The printed witness remains the source of readings. SVG supplies a useful
connection between the visual result and the editable encoding.

## What the research supports

Your positive experience fits a real research direction. **VGBench** (EMNLP
2024) already tested vector graphics supplied as text, including understanding
and comparison with raster-based vision. It found useful capabilities, with
greater difficulty for low-level SVG than more explicit representations.
This establishes that reading vector code is a meaningful task, not merely
an incidental ability to produce XML.
[Paper](https://aclanthology.org/2024.emnlp-main.213/).

**SVGenius** (June 2025) separates understanding, editing and generation over
2,377 queries. Its results show substantial SVG editing/understanding ability,
particularly in proprietary models, and a strong dependence on complexity.
Its tested models include GPT-4o, Claude 3.7 Sonnet and Gemini 2.0 Flash, so it
is historical evidence rather than a ranking of today's frontier models.
[Paper and results](https://arxiv.org/html/2506.03139v1).

**VectorGym**, revised August 2026, is closer to the practical workflow: its
human-authored editing tasks include path modifications and conceptual changes,
rather than just colour/scale adjustments. It evaluates Gemini 3 Pro, Claude
Sonnet 4.5 and GPT-5.1 among others, and combines rendered-image comparisons with
model judgments. This supports treating visual/code editing as a practical
capability. Its aggregate scores are task-specific scores, not percentages of
correct musical edits. Some narrative scores differ within the paper, so they
are not used here as a precise model-selection rule.
[Revised paper](https://arxiv.org/html/2603.29852v2).

**SVGEval** (August 2026) specifically studies judging the rendered outcome. It
finds that semantic/aesthetic assessment is easier than precise geometric and
spatial assessment, and investigates explicit SVG information alongside visual
grounding. This makes an edit–render–inspect loop a well-motivated experiment;
it does not establish that a model can approve a slur endpoint reliably.
[Paper](https://arxiv.org/html/2608.01977v1).

For a current, accessible demonstration of frontier SVG generation, Rapidata's
live **SVG generation leaderboard** includes recent frontier models and exposes
its methodology/data. It ranks human preference between generated designs.
Use it to show what models can draw; it does not measure reading an existing
score or preserving MEI references.
[Leaderboard/methodology](https://www.benchmark.ai/svg),
[dataset documentation](https://huggingface.co/datasets/Rapidata/text-to-svg-human-feedback-benchmark/blob/main/README.md).

For music specifically, **MSU-Bench** (ACL 2026) evaluates 1,800 questions across
ABC and PDF score inputs, reporting substantial differences between symbolic
and visual reasoning. It does not test Verovio SVG or source-based editorial
patches. It supports giving the model musical structure as well as images,
while keeping the musical task explicit.
[Published paper](https://aclanthology.org/2026.acl-long.493/).

These sources support the capability and workflow. They do not provide a
controlled longitudinal measurement of improvement on this Schumann task.
The useful seminar question is: **does structured SVG help this model make
and explain a correct, source-based edit?**

## Three meanings of “understanding SVG”

1. **Reading SVG source as text:** groups, classes, IDs, transforms, paths and
   glyph references are tokens the model can inspect. This works in principle
   with a text/code model, without using an image encoder.
2. **Seeing a rasterized SVG:** a tool or editor renders the SVG to an image
   that a vision model inspects. The image conveys appearance, while raw DOM
   IDs and attributes are available only if supplied separately.
3. **Using SVG with musical metadata:** Verovio's groups connect notation to
   existing MEI IDs. Its `svgAdditionalAttribute` option can add encoded MEI
   values as `data-*` attributes, for example `note@pname` → `data-pname`.
   This gives a model explicit musical hints beside the graphics.
   [Verovio options](https://book.verovio.org/toolkit-reference/toolkit-options.html).

The third route is especially attractive for your edition workflow. Our local
Verovio 6.3 test produces, for the pickup:

```xml
<g id="d1e60" class="note" data-pname="c" data-oct="3" data-dur="8">
  <!-- notehead, stem and other graphics -->
</g>
```

This is an illustrative abbreviated snippet; the generated SVG retains its
actual glyph definitions. The ID is a stable address back into the MEI.
The attributes copy the **current encoding**, including any mistakes. They do
not independently confirm the print. Pitch spelling also needs key/accidental
context; duration may be carried by a containing chord. Enriched SVG is an
assisted representation, not a blind visual-reading test.

An SVG attachment is not automatically an SVG-text input. For example, OpenAI's
documented image-input formats are PNG/JPEG/WEBP/non-animated GIF; SVG source
must be supplied as text/file context or rendered using a tool.
[Image-input documentation](https://developers.openai.com/api/docs/guides/images-vision).
In any VS Code extension, record whether the model actually received source
text, a raster preview, both, or an unknown transformation. An editor preview
alone does not establish model input.

## The editorial loop to demonstrate

Use four connected objects: **source scan → current MEI → SVG/PNG engraving →
candidate MEI and its new engraving**. The model can:

- compare one printed system with the current engraving;
- identify a missing/wrong mark and tie its location to existing IDs;
- distinguish an encoding discrepancy from a rendering/placement problem;
- apply a small candidate patch, run structural/schema checks and re-render;
- explain the evidence and the remaining uncertainty for editorial review.

This is a useful semi-automated workflow: bounded local execution is part of the
exercise, not just asking a chatbot to return an XML fragment. Keep the working
file and source untouched while trying a candidate. The reviewer accepts the
reading and its encoded attachment after inspecting the source, diff and result.

Your Webern edition supplies a concrete case study: its editorial policy
describes system-by-system scan/render comparison and targeted MEI repairs;
`render_variants.py` compares alternative encodings in memory. Its encoding
profile documents a grace-slur rendering compromise in III/15 and III/18:
the exact note endpoint is retained and the display workaround is annotated.
That is an excellent short example of why a plausible picture alone does not
settle the editorial attachment. These are repo-documented workflow examples,
not a quantitative estimate of model accuracy.
[Webern viewer](https://egorpol.github.io/webern_op27/).

## Fit it into Block 2 without adding time

Keep minutes **0–10** for the live viewer. Replace the previous optional
two-model forte comparison with a source-aware SVG demonstration:

- **10–18:** use the [beginner SVG showcase](svg-introduction.md): change a
  circle, enlarge PNG/vector versions, then connect a drawn note with its MEI
  ID. Extra attributes and the Webern example are optional after that connection
  is clear. No path syntax, CSS or glyph knowledge is assumed.
- **18–23:** restore the opening tempo/dynamic manually. Everyone experiences
  save → refresh before delegating a small task.
- **23–32:** ask a model to inspect the **two opening slur phrases** from the
  scan and current engraving, locate the endpoints and draft a candidate patch.
  Give first-system context and MEI labels 1–5; restrict the task to the pickup
  and first two full bars (labels 1–3). Do not supply the answer-key endpoints
  in this visual-reading prompt. It may return an unresolved reading instead.
- **32–40:** inspect the evidence/IDs, validate and re-render one candidate,
  then add a short anchored annotation. Accept/correct/reject the patch and
  explain why. Keep the second-system forte prompt as the text-only fallback.

The existing mei-friend (40–50), peer review (50–65) and release (65–90)
segments retain their time. A prepared instructor demonstration works if
students' free accounts cannot attach images. Access and capability are
different: the free-model handout is not an SVG/music-accuracy ranking.

## A small, fair classroom experiment

Use the **same model**, same prompt, same images and same MEI context in fresh
chats, with a common starting checkpoint:

- **A:** source PNG + engraving PNG + MEI context.
- **B:** A + default SVG source, explicitly supplied as text/file context.
- **C, optional:** A + enriched SVG source, replacing the default SVG.

Pairs can optionally split A/B and pool observations, or use this as a follow-up.
The core eight-minute introduction and one candidate task take priority. This varies the representation
instead of changing model and representation together. C repeats musical values
already present in MEI in a more explicit place; it measures useful scaffolding,
not pure perception. A small classroom sample supports discussion, not a robust
leaderboard. Keep token/cost/latency observations separate from correctness.

Evaluate whether the model found the two printed phrase divisions, chose the
correct staff and exact endpoint IDs, preserved existing content/links, passed
validation, and explained the source-based decision. Also record unexpected
changes, missed marks and human corrections. Do not use whole-image similarity
as the editorial success criterion.

The [packet notebook](../../02-building-an-edition/notebooks/02_svg_editorial.ipynb) creates the current
SVGs/PNG, read-only MEI context, system crop, prompts and a record template.
Glyph definitions are retained; a selected SVG is rendered through Verovio
rather than cut out of the DOM by hand.
[Content selection](https://book.verovio.org/interactive-notation/content-selection.html).
It makes no provider calls. Generated scan-bearing files stay in the ignored
working project; the [reference evidence](../../02-building-an-edition/teacher/references/svg-editorial/README.md)
records what was actually tested locally.
