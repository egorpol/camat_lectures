# What is SVG? An introduction for musicology students

Use the [interactive browser demos](../../02-building-an-edition/examples/svg-introduction/index.html)
before the [SVG editorial exercise](svg-editorial-workflow.md). They work
offline, with no installation, model account or previous Schumann project.
For editable notebook versions, use
[02_what_is_svg.ipynb](../../02-building-an-edition/notebooks/02_what_is_svg.ipynb) with the separate
[asset ZIP](../../02-building-an-edition/notebooks/svg-introduction-assets.zip).

**Say first:** “SVG is a picture described with text. The browser reads that
description and draws lines and shapes. MEI describes the music we want the
engraver to draw.” SVG stands for *Scalable Vector Graphics* and uses XML-style
tags and attributes. [MDN introduction](https://developer.mozilla.org/en-US/docs/Web/SVG).

The aim is to recognise the connection, not to learn a graphics programming
language. Students only need four words: **element**, **attribute**, **group**
and **ID** (an address).

## An eight-minute showcase

**10–12: change a picture.** Show a circle with its three-line SVG description.
Ask someone to choose another colour. Change `fill="black"` to blue; move the
position slider. The picture and visible text update together. Explain one tag
and one attribute. Ask: “What did the browser need to know to draw this?”

**12–14: zoom a note.** Enlarge the same simple note drawing as a 32 × 32 PNG
and as SVG. Reveal the PNG's pixel grid, then turn smoothing back on. Explain
fixed pixels versus shapes redrawn at the display size. Both examples are our
own demonstration graphic; neither is a source scan. An SVG can contain a
raster image, and PDFs may contain scans or vector drawings.

**14–18: connect a real note to MEI.** Show Schumann's pickup and click the bass
note. Its SVG group and MEI share address `d1e60`. Read only the short note
element: C, octave 3, eighth note. Highlight it: the pitch stays C3. Switch the
prepared MEI example from C3 to F3 and show the new engraving with the same ID.
Explain that this is an artificial teaching change, not a correction to the
edition. Verovio preserves MEI IDs and grouping in SVG.
[Verovio tutorial](https://book.verovio.org/interactive-notation/css-and-svg.html).

End with: “A model can inspect the picture and name the exact encoding target.
We give it the source scan too, because the current engraving shows our current
encoding.” Hide the optional musical `data-*` attributes until this connection
is clear. Leave path coordinates, transforms, CSS and glyph definitions for an
optional follow-up; the renderer handles those for this exercise.

## Keep the session within 90 minutes

The editing loop remains **0–10**. Use the primer at **10–18**, manual opening
marks at **18–23**, a single model-assisted slur task at **23–32**, and candidate
review/annotation at **32–40**. The A/B representation comparison is an optional
pair split or follow-up; the full same-pair comparison need not fit this slot.
Mei-friend, peer review and release retain their existing times.

For a five-minute instructor-only version, spend one minute on each of the first
two demos and three on the MEI/score connection. For students trying controls
and explaining them to a neighbour, use the full eight-minute version.

## Student takeaway and a tiny exercise

“MEI says what the musical event is. SVG describes how the engraving is drawn.
An ID lets us connect a drawn symbol with the corresponding encoded event.”
This is a useful division of roles, not a claim that SVG cannot carry metadata.

Ask pairs to answer the three questions at the bottom of the demo. If time
allows, let them edit the circle cell in the notebook, run it, and explain
which value changed. They can also open `note-symbol.svg` as text and as a
picture. No handwritten notehead paths or complete SVG score are required.

To use the browser demo locally, unzip `svg-introduction-assets.zip` into a new
folder and open its **index.html**, keeping the other files beside it. A normal
browser runs its controls; Jupyter's HTML preview may disable JavaScript. The
notebook offers the same concepts through editable cells and preserves existing
extracted files. It does not call Verovio, CAMAT or a model service at runtime.

The prepared pitch variants and recorded checks are explained in
[the demo notes](../../02-building-an-edition/examples/svg-introduction/README.md).
