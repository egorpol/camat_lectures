"""Drive the session-2 demos in headless Chromium and print what they show.

Usage (from the repository root):
    .venv/bin/mkdocs build -d site
    .venv/bin/python tools/check_site_s2.py [screenshot_dir]

Needs `pip install playwright` and `playwright install chromium`. The compare
demo fetches the MEI Sample Collection file from GitHub, so it needs network
access. Runs at 1280 and 390 px. Expected on 2026-10-27: in both views (pickup
and bar 1; bar 5) both panes show the same measures (d1e9,d1e74; d1e1231), the
target note (d1e338; d1e1495) filled rgb(21, 101, 192), captions A3 on the
left and F3 on the right, no visible measure number. The ABC box starts with
"Pickup: C3 eighth"; the solution reads "Bar 1: F3 dotted quarter, A3 eighth,
C4 dotted quarter, F3 eighth"; without the commas F4, A4, C4, F4; an unfinished
bar "(2 of 4 quarter notes)"; a rest "rest half"; no K: line gives the
precheck error; Reset goes back to the pickup. Each edit renders in about
0.8 s (400 ms of it the typing pause). The *Any format* box detects abc (an
LLM answer in a code fence), mei (opened as a file), xml, humdrum and pae, and
reads the solution's notes from each; plain words get "Which format is
this?". The inspect demo has 22 selectable notes/rests; on load d1e338 is
highlighted rgb(21, 101, 192) with panel "F3, eighth", its MEI tag and SVG
group (inside it: notehead, stem, flag; Verovio nests the flag in the stem);
click d1e60 → C3 eighth (notehead, stem, flag); d1e224 → C5 eighth (chord
note, SVG inside notehead only); d1e30 → Rest eighth (no "inside it");
keyboard Enter on d1e323 → C4 dotted quarter (notehead, dots, stem); exactly one highlight,
no visible measure number. No page overflow, no console errors.

The "What is SVG?" page (svg/) is checked in light and dark at both widths,
with assertions: each failure prints "FAIL: ..." and the script exits 1.
The sidebar lists both sessions as plain links (Material's navigation.indexes
once swallowed session 1). Circle: the code text follows colour, position and radius, the drawn circle
is royalblue, Reset goes back to black/70/22. Zoom: 12× gives both images
384 px, the slider does not move between 1× and 12×, the box switches
pixelated/auto. Note d1e60: unhighlighted black, its SVG text has no fill and
none of the demo's own attributes; highlighted, notehead, stem and flag are
royalblue and the SVG text gains exactly fill="royalblue" color="royalblue"
(the attribute alone colours it: set to crimson, it turns crimson); F3 moves
the note up, keeps d1e60, the highlight and the other notes, MEI text
pname="f"; extra attributes add data-pname/oct/dur; Reset gives C3
unhighlighted. Paper behind the circle, zoom images and score is white in
both schemes.
"""

import functools
import http.server
import sys
import tempfile
import threading
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "site"
OUT = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="check_site_s2_")
SCAFFOLD = (SITE / "sessions/02-building-an-edition/examples/schumann/pickup-bar1.abc").read_text()


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{server.server_address[1]}/sessions/02-building-an-edition/"


def pixels(path):
    """Share of dark and of highlight-blue pixels: a blank render has neither."""
    img = Image.open(path).convert("RGB")
    px = list(img.get_flattened_data())
    dark = sum(1 for r, g, b in px if r + g + b < 200) / len(px)
    blue = sum(1 for r, g, b in px if b > 150 and r < 80 and 80 < g < 130) / len(px)
    return f"dark {dark:.3f}, blue {blue:.4f}"


ABC_BOX = "[data-demo=edit][data-format=abc]"
ANY_BOX = "[data-demo=edit][data-format=auto]"
SOLUTION = "C, | F,3 A, C3 F, |]\n"
MEI = Path("tools/notebooks/02_note_entry.py").read_text().split('mei = """', 1)[1].split('"""', 1)[0]
MUSICXML = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0"><part-list><score-part id="P1"><part-name>Bass</part-name></score-part></part-list>
<part id="P1"><measure number="0" implicit="yes"><attributes><divisions>2</divisions><key><fifths>-1</fifths></key>
<time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>F</sign><line>4</line></clef></attributes>
<note><pitch><step>C</step><octave>3</octave></pitch><duration>1</duration><type>eighth</type></note></measure>
<measure number="1"><note><pitch><step>F</step><octave>3</octave></pitch><duration>3</duration><type>quarter</type><dot/></note>
<note><pitch><step>A</step><octave>3</octave></pitch><duration>1</duration><type>eighth</type></note>
<note><pitch><step>C</step><octave>4</octave></pitch><duration>3</duration><type>quarter</type><dot/></note>
<note><pitch><step>F</step><octave>3</octave></pitch><duration>1</duration><type>eighth</type></note></measure></part></score-partwise>
"""


def reads(page, box=ABC_BOX):
    return page.eval_on_selector_all(f"{box} .edit-reads li", "ls => ls.map(l => l.textContent)")


def type_and_wait(page, text, box=ABC_BOX, file=None):
    before = page.eval_on_selector(f"{box} .vrv-out", "e => e.innerHTML.length")
    if file:
        page.set_input_files(f"{box} input[type=file]", file)
    else:
        page.fill(f"{box} textarea", text)
    t0 = time.time()
    page.wait_for_function(f"document.querySelector('{box} .vrv-out').innerHTML.length !== {before}", timeout=30000)
    page.wait_for_timeout(300)
    return time.time() - t0


FAILS = []


def expect(ok, what):
    if not ok:
        FAILS.append(what)
        print(f"FAIL: {what}")


SVG_NOTE = "[data-demo=svg-note]"
# Colours of the note's parts and the texts of the two panes, read from the page.
NOTE_STATE = """() => {
    const root = document.querySelector('[data-demo=svg-note]');
    const g = root.querySelector('g[id="d1e60"]');
    const pres = [...root.querySelectorAll('pre')].map(p => p.textContent);
    const cs = (sel, prop) => { const e = g?.querySelector(sel); return e ? getComputedStyle(e)[prop] : null; };
    return {
        found: !!g,
        attrs: g ? [g.getAttribute('fill'), g.getAttribute('color')] : null,
        notehead: cs('g.notehead use', 'fill'), stem: cs('g.stem > path', 'stroke'), flag: cs('g.flag use', 'fill'),
        y: g ? g.querySelector('g.notehead').getBoundingClientRect().y : null,
        notes: [...root.querySelectorAll('g.note')].map(n => n.id).join(','),
        mei: pres.find(t => t.includes('<note')) ?? '',
        svg: pres.find(t => t.includes('<g')) ?? '',
    };
}"""
# First non-transparent background behind an element: the "paper" it sits on.
PAPER = """el => { for (let e = el; e; e = e.parentElement) {
    const bg = getComputedStyle(e).backgroundColor;
    if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') return bg; } return null; }"""
BLUE, BLACK, WHITE = "rgb(65, 105, 225)", "rgb(0, 0, 0)", "rgb(255, 255, 255)"


def set_range(page, locator, value):
    locator.evaluate("(e, v) => { e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); }", str(value))
    page.wait_for_timeout(100)


def check_svg_page(b, width, height, scheme):
    logs = []
    ctx = b.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
    page = ctx.new_page()
    page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"[:200]) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"[:300]))
    tag = f"svg page {width} {scheme}"
    response = page.goto(URL + "svg/")
    print(f"== {tag}")
    if not response or not response.ok:
        expect(False, f"{tag}: page not found")
        ctx.close()
        return
    expect(page.get_attribute("body", "data-md-color-scheme") == ("slate" if scheme == "dark" else "default"),
           f"{tag}: Material scheme")
    if width >= 1220:  # Material shows the left sidebar from 76.25em
        side = page.locator(".md-sidebar--primary .md-nav__link:visible").all_inner_texts()
        expect(all(any(t.strip() == want for t in side) for want in ["1. Why encode music?", "2. The source and the notes"]),
               f"{tag}: sidebar lists both sessions {side}")

    # 1. Circle
    circ = page.locator("[data-demo=svg-circle]")
    circ.scroll_into_view_if_needed()
    page.wait_for_selector("[data-demo=svg-circle] pre")
    ranges = circ.locator("input[type=range]")
    circ.locator("select").select_option("royalblue")
    set_range(page, ranges.nth(0), 150)
    set_range(page, ranges.nth(1), 30)
    code = circ.locator("pre").inner_text()
    drawn = circ.locator("circle").last
    print("circle code:", " ".join(code.split()))
    expect(all(s in code for s in ['cx="150"', 'r="30"', 'fill="royalblue"']), f"{tag}: circle code follows controls")
    expect(drawn.evaluate("e => getComputedStyle(e).fill") == BLUE and drawn.get_attribute("cx") == "150",
           f"{tag}: drawn circle royalblue at 150")
    expect(drawn.evaluate(PAPER) == WHITE, f"{tag}: circle on white paper")
    circ.locator("button", has_text="Reset").click()
    page.wait_for_timeout(100)
    code = circ.locator("pre").inner_text()
    expect(all(s in code for s in ['cx="70"', 'r="22"', 'fill="black"']), f"{tag}: circle Reset")

    # 2. Zoom
    zoom = page.locator("[data-demo=svg-zoom]")
    zoom.scroll_into_view_if_needed()
    slider, img, vec = zoom.locator("input[type=range]"), zoom.locator("img"), zoom.locator("svg").last
    set_range(page, slider, 1)
    x1 = slider.bounding_box()["x"]
    set_range(page, slider, 12)
    x12 = slider.bounding_box()["x"]
    sizes = [img.evaluate("e => e.getBoundingClientRect().width"), vec.evaluate("e => e.getBoundingClientRect().width")]
    print(f"zoom 12x sizes {sizes}, slider x {x1} -> {x12}")
    expect(sizes == [384, 384], f"{tag}: zoom 12x gives 384 px")
    expect(abs(x1 - x12) < 1, f"{tag}: slider stays put")
    box = zoom.locator("input[type=checkbox]")
    rendering = [img.evaluate("e => getComputedStyle(e).imageRendering")]
    box.click()
    page.wait_for_timeout(100)
    rendering.append(img.evaluate("e => getComputedStyle(e).imageRendering"))
    expect(rendering == ["pixelated", "auto"], f"{tag}: pixel grid box {rendering}")
    expect(img.evaluate(PAPER) == WHITE and vec.evaluate(PAPER) == WHITE, f"{tag}: zoom on white paper")

    # 3. The note
    note = page.locator(SVG_NOTE)
    note.scroll_into_view_if_needed()
    page.wait_for_selector(f'{SVG_NOTE} g[id="d1e60"]', timeout=90000)
    page.wait_for_timeout(300)
    state = lambda: page.evaluate(NOTE_STATE)
    s0 = state()
    print("note load:", s0["notehead"], "| MEI:", s0["mei"], "| SVG:", " ".join(s0["svg"].split()))
    expect(s0["notehead"] == BLACK and s0["attrs"] == [None, None], f"{tag}: note starts black")
    expect('pname="c"' in s0["mei"] and 'xml:id="d1e60"' in s0["mei"], f"{tag}: MEI pane C3")
    expect('id="d1e60"' in s0["svg"] and 'class="note"' in s0["svg"], f"{tag}: SVG pane id and class")
    expect(not any(w in s0["svg"] for w in ["fill", "color", "tabindex", "role", "aria"]), f"{tag}: SVG pane clean")
    expect(page.locator(f'{SVG_NOTE} g[id="d1e60"]').evaluate(PAPER) == WHITE, f"{tag}: score on white paper")
    note.locator("button", has_text="Highlight").click()
    page.wait_for_timeout(200)
    s1 = state()
    print("highlighted:", s1["notehead"], s1["stem"], s1["flag"], "| SVG:", " ".join(s1["svg"].split()))
    expect([s1["notehead"], s1["stem"], s1["flag"]] == [BLUE] * 3, f"{tag}: whole note royalblue")
    expect('fill="royalblue"' in s1["svg"] and 'color="royalblue"' in s1["svg"], f"{tag}: SVG pane shows fill/color")
    expect(s1["mei"] == s0["mei"], f"{tag}: MEI pane unchanged by highlight")
    page.evaluate("""() => { const g = document.querySelector('[data-demo=svg-note] g[id="d1e60"]');
        g.setAttribute('fill', 'crimson'); g.setAttribute('color', 'crimson'); }""")
    probe = state()
    expect([probe["notehead"], probe["stem"]] == ["rgb(220, 20, 60)"] * 2, f"{tag}: attributes alone colour the note")
    page.evaluate("""() => { const g = document.querySelector('[data-demo=svg-note] g[id="d1e60"]');
        g.setAttribute('fill', 'royalblue'); g.setAttribute('color', 'royalblue'); }""")
    page.locator(f'{SVG_NOTE} g[id="d1e60"]').click(force=True)
    page.wait_for_timeout(200)
    s2 = state()
    expect(s2["attrs"] == [None, None] and "fill" not in s2["svg"], f"{tag}: click on note turns highlight off")
    page.locator(f'{SVG_NOTE} g[id="d1e60"]').focus()
    page.keyboard.press("Enter")
    page.wait_for_timeout(200)
    expect(state()["attrs"] == ["royalblue", "royalblue"], f"{tag}: Enter turns highlight on")
    note.locator("select").select_option(index=1)
    page.wait_for_function(f"""document.querySelector('{SVG_NOTE}') &&
        [...document.querySelectorAll('{SVG_NOTE} pre')].some(p => p.textContent.includes('pname="f"'))""", timeout=30000)
    page.wait_for_timeout(300)
    s3 = state()
    print(f"F3: notehead y {s0['y']:.0f} -> {s3['y']:.0f} | MEI:", s3["mei"])
    expect(s3["found"] and s3["y"] < s0["y"], f"{tag}: F3 moves d1e60 up")
    expect(s3["attrs"] == ["royalblue", "royalblue"] and 'fill="royalblue"' in s3["svg"], f"{tag}: F3 keeps highlight")
    expect(s3["notes"] == s0["notes"], f"{tag}: F3 keeps the other notes")
    note.locator("input[type=checkbox]").click()
    page.wait_for_function(f"""[...document.querySelectorAll('{SVG_NOTE} pre')].some(p => p.textContent.includes('data-pname'))""",
                           timeout=30000)
    s4 = state()
    print("extra:", " ".join(s4["svg"].split()))
    expect(all(a in s4["svg"] for a in ['data-pname="f"', 'data-oct="3"', 'data-dur="8"']), f"{tag}: extra attributes")
    note.locator("button", has_text="Reset").click()
    page.wait_for_function(f"""[...document.querySelectorAll('{SVG_NOTE} pre')].some(p => p.textContent.includes('pname="c"'))""",
                           timeout=30000)
    page.wait_for_timeout(300)
    s5 = state()
    expect(s5["attrs"] == [None, None] and "data-pname" not in s5["svg"] and s5["svg"] == s0["svg"], f"{tag}: Reset")

    shot = f"{OUT}/svg_{scheme}_{width}.png"
    page.screenshot(path=shot, full_page=True)
    sw, cw = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    expect(sw <= cw, f"{tag}: page overflow {sw} > {cw}")
    errors = [line for line in logs if not line.startswith("warning")]
    expect(not errors, f"{tag}: console {errors}")
    print("console:", logs)
    ctx.close()


with sync_playwright() as p:
    b = p.chromium.launch()
    for width, height in [(1280, 900), (390, 844)]:
        logs = []
        ctx = b.new_context(viewport={"width": width, "height": height})
        page = ctx.new_page()
        page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"[:200]) if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"[:300]))
        page.goto(URL)
        print(f"== {width} px")
        # Part 3: compare
        cmp_ = page.locator("[data-demo=compare]")
        cmp_.scroll_into_view_if_needed()
        page.wait_for_function("document.querySelectorAll('[data-demo=compare] .vrv-score > svg').length === 2", timeout=90000)
        for label in ["Pickup and bar 1", "Bar 5"]:
            cmp_.get_by_role("button", name=label).click()
            page.wait_for_timeout(200)
            panes = page.eval_on_selector_all("[data-demo=compare] .cmp-pane", """ps => ps.map(p => {
                const t = p.querySelector('.cmp-target');
                return {title: p.querySelector('.vrv-label').textContent,
                        measures: [...p.querySelectorAll('g.measure')].map(m => m.id).join(','),
                        target: t ? t.id + ' ' + getComputedStyle(t).fill : 'NONE',
                        caption: p.querySelector('.vrv-note')?.textContent,
                        mnum: [...p.querySelectorAll('g.mNum')].filter(g => getComputedStyle(g).display !== 'none').length};
            })""")
            print(f"compare {label}: pressed={cmp_.get_by_role('button', name=label).get_attribute('aria-pressed')}")
            for pane in panes:
                print("  ", pane)
            shot = f"{OUT}/compare_{width}_{label.replace(' ', '_')}.png"
            cmp_.screenshot(path=shot)
            print("   pixels:", pixels(shot))
        # Part 5: ABC box
        ed = page.locator(ABC_BOX)
        ed.scroll_into_view_if_needed()
        page.wait_for_function(f"document.querySelector('{ABC_BOX} .vrv-score svg')", timeout=90000)
        page.wait_for_timeout(300)
        print("edit start:", reads(page))
        cases = [
            ("solution", SCAFFOLD.replace("C, |\n", SOLUTION)),
            ("no commas", SCAFFOLD.replace("C, |\n", "C, | F3 A C3 F |]\n")),
            ("unfinished", SCAFFOLD.replace("C, |\n", "C, | F,3 A, |\n")),
            ("rest", SCAFFOLD.replace("C, |\n", "C, | F,3 A, z4 |]\n")),
            ("no K: line", SCAFFOLD.replace("K:F clef=bass\n", "")),
        ]
        for name, text in cases:
            dt = type_and_wait(page, text)
            msgs = page.eval_on_selector_all(f"{ABC_BOX} .vrv-messages li", "ls => ls.map(l => l.textContent)")
            print(f"edit {name} ({dt:.2f} s):", reads(page), msgs or "")
            if name == "solution":
                shot = f"{OUT}/edit_{width}_solution.png"
                ed.screenshot(path=shot)
                print("   pixels:", pixels(shot))
        ed.get_by_role("button", name="Reset").click()
        page.wait_for_timeout(1500)
        print("edit after Reset:", reads(page))
        # Part 5: the Any format box (MuseScore exports, LLM answers)
        page.locator(ANY_BOX).scroll_into_view_if_needed()
        cases = [
            ("LLM answer", "```abc\n" + SCAFFOLD.replace("C, |\n", SOLUTION) + "```\n", None),
            ("MEI file", None, {"name": "notes.mei", "mimeType": "text/xml", "buffer": MEI.encode()}),
            ("MusicXML", MUSICXML, None),
            ("kern", "**kern\n*clefF4\n*k[b-]\n*M4/4\n8C\n=1\n4.F\n8A\n4.c\n8F\n==\n*-\n", None),
            ("PAE", "@clef:F-4\n@keysig:bB\n@timesig:4/4\n@data:,8C/4.F8A'4.C,8F//\n", None),
            ("words", "C3 eighth, F3 dotted quarter", None),
        ]
        for name, text, file in cases:
            dt = type_and_wait(page, text, ANY_BOX, file)
            label = page.inner_text(f"{ANY_BOX} header code")
            note = page.inner_text(f"{ANY_BOX} .vrv-out").strip()[:40] if not reads(page, ANY_BOX) else ""
            print(f"any {name} ({dt:.2f} s): {label}", reads(page, ANY_BOX), note)
        # Part 7: inspect
        insp = page.locator("[data-demo=inspect]")
        insp.scroll_into_view_if_needed()
        page.wait_for_function("document.querySelector('[data-demo=inspect] .vrv-score svg')", timeout=90000)
        page.wait_for_timeout(300)
        n_sel = page.eval_on_selector_all('[data-demo=inspect] [tabindex="0"]', "els => els.length")
        print(f"inspect selectable: {n_sel}")

        def insp_state():
            return page.evaluate("""() => {
                const root = document.querySelector('[data-demo=inspect]');
                const t = root.querySelector('.insp-target');
                const lines = [...root.querySelectorAll('.insp-panel p')].map(p => p.textContent);
                const hi = [...root.querySelectorAll('.insp-target')].length;
                const mnum = [...root.querySelectorAll('g.mNum')]
                    .filter(g => getComputedStyle(g).display !== 'none').length;
                return {
                    id: t?.id,
                    fill: t ? getComputedStyle(t).fill : null,
                    lines,
                    highlighted: hi,
                    mnum,
                };
            }""")

        state = insp_state()
        print(f"inspect load: {state['id']} {state['fill']}")
        for line in state["lines"]:
            print(f"  {line}")
        for note_id, label in [("d1e60", "bass C3"), ("d1e224", "chord C5"), ("d1e30", "rest")]:
            page.locator(f'[data-demo=inspect] g[id="{note_id}"]').click(force=True)
            page.wait_for_timeout(100)
            state = insp_state()
            print(f"inspect click {note_id} ({label}): {state['id']} {state['fill']}")
            for line in state["lines"]:
                print(f"  {line}")
        page.locator('[data-demo=inspect] g[id="d1e323"]').focus()
        page.keyboard.press("Enter")
        page.wait_for_timeout(100)
        state = insp_state()
        print(f"inspect Enter d1e323: {state['id']} {state['fill']}")
        for line in state["lines"]:
            print(f"  {line}")
        print(f"inspect highlighted={state['highlighted']} mnum={state['mnum']}")
        shot = f"{OUT}/inspect_{width}.png"
        insp.screenshot(path=shot)
        print("   pixels:", pixels(shot))
        sw, cw = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        print("page overflow:", "none" if sw <= cw else f"{sw} > {cw}")
        print("console:", logs)
        ctx.close()
        for scheme in ("light", "dark"):
            check_svg_page(b, width, height, scheme)
    b.close()
print("screenshots:", OUT)
print(f"svg page: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
