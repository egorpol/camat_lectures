# What is SVG?

SVG (Scalable Vector Graphics) is a picture described as text: your browser reads the description and draws it. Verovio draws every score on this site as SVG. This page has three short demos. Back to [session 2, part 7](index.md#7-the-note-in-the-mei-file).

## 1. Text becomes a picture

`<circle>` means "draw a circle". In it, `fill` gives the colour, `cx` the horizontal position and `r` the radius. Change them and watch the text and the picture.

<div data-demo="svg-circle"></div>

The text and the picture describe the same circle in two ways: change a value in the text, and the picture changes with it.

??? info "Three words we will use"
    A **tag**, such as `<circle>`, names an element. An **attribute**, such as `fill="black"`, gives it a property. A **group**, `<g>…</g>`, keeps several elements together.

## 2. Why "scalable"?

The same note symbol twice: on the left as a PNG, a grid of 32 × 32 coloured squares (pixels); on the right as SVG, an oval and a line. Enlarge both.

<div data-demo="svg-zoom" data-png="../examples/svg-introduction/note-32px.png"></div>

The PNG has only its 32 × 32 squares: enlarged, they become large blocks (untick the box to see the browser's usual smoothing, which blurs them instead). The SVG is drawn again at every size, so it stays sharp.

??? info "Does saving a scan as SVG make it sharper?"
    No. An SVG can contain a pixel image, in an `<image>` element, and that image keeps its pixels. A PDF, too, can contain either a scan or vector drawings. The file name alone does not tell you which is inside.

## 3. One note, two descriptions, the same address

Here is the pickup of our starting file: a C3, an eighth note, in the lower staff. Verovio draws it as SVG and keeps its address, `d1e60`. Click the note, or the button, to highlight it, and compare the two texts under the score.

<div data-demo="svg-note" data-file="../examples/schumann/starter.mei" data-note="d1e60"></div>

- **Highlight:** the SVG group gets two new attributes, `fill` (the colour of the notehead and the flag) and `color` (the colour of the stem). The MEI does not change: the note is still a C3, an eighth note. Colour is appearance, not music.
- **MEI pitch F3:** we change one attribute in the MEI, `pname="c"` to `pname="f"`, and Verovio draws the note again. It moves up; its address `d1e60` stays the same. F3 is only an experiment for this page, not a correction to Schumann.
- **Extra attributes:** Verovio can copy some MEI values into the SVG as `data-…` attributes. They are copies; the pitch is recorded in the MEI.

The SVG text shows the drawing in your browser as it is now; no file changes.

??? info "Why can an AI model use this?"
    A model can look at the drawn score and use the SVG addresses to name the exact note in the MEI. The `data-…` attributes only repeat what the MEI says; they do not check it against the scan. In the next session's editing exercise, the model gets the scan, the drawn score and the MEI together.

## Three questions

1. If we colour a note blue, have we changed its pitch?
2. Which file records C3 and its length: the MEI or the SVG drawing?
3. When the drawn score differs from the printed source, which one do we check for the reading?

??? success "Suggested answers"
    1. No. Colour changes the drawing (the SVG), not the music (the MEI).
    2. The MEI. An SVG can repeat some MEI values as `data-…` attributes, but they are copies.
    3. The printed source, our witness. Then we check how the MEI encodes that reading and how Verovio draws it.

**Background:** [MDN's SVG pages](https://developer.mozilla.org/en-US/docs/Web/SVG) · [SVG in the Verovio book](https://book.verovio.org/interactive-notation/css-and-svg.html)

The score is the pickup of our starting file, [`starter.mei`](examples/schumann/starter.mei){: download="starter.mei" }; its sources are listed at the end of the [session page](index.md#sources).
