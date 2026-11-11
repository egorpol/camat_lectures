"""Check the session-2 record and the SVG demos in headless Chromium.

Usage (from the repository root):
    .venv/bin/mkdocs build --strict -d site
    .venv/bin/python tools/check_site_s2.py [screenshot_dir]

Needs `pip install playwright` and `playwright install chromium`. The SVG
note demo loads Verovio, so it needs network access. Runs at 1280 and 390 px.
The session page must have the ten expected h2 headings in order and no
[data-demo] elements. Every same-site link on both pages must return HTTP 200
from the local server; fragments must name an element in the target page.
Both pages must have no horizontal overflow or console errors. Full-page
screenshots are saved for each width, with the SVG page in light and dark.

The "What is SVG?" page (svg/) retains its demo assertions. The sidebar lists
both sessions as plain links. Circle: the code follows colour, position and
radius; Reset restores black/70/22. Zoom: 12× gives both images 384 px, the
slider stays put, and the checkbox switches pixelated/auto. Note d1e60 starts
black with clean SVG text; highlighting colours notehead, stem and flag and
adds fill/color without changing MEI. F3 moves the note up while keeping its
id, highlight and other notes. Extra attributes add data-pname/oct/dur; Reset
restores C3 without highlighting. Paper stays white in both colour schemes.

Each failed assertion prints "FAIL: ...". The final failure count covers both
pages; the script exits 1 if any assertion failed, otherwise 0.
"""

import functools
import http.server
import sys
import tempfile
import threading
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlsplit

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "site"
OUT = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="check_site_s2_")
Path(OUT).mkdir(parents=True, exist_ok=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{server.server_address[1]}/sessions/02-building-an-edition/"
FAILS = []


def expect(ok, what):
    if not ok:
        FAILS.append(what)
        print(f"FAIL: {what}")


HEADINGS = [
    "1. Setup",
    "2. Source, scan, encoding, edition",
    "3. The page and its bars",
    "4. From a scan to notes: OMR",
    "5. The score as SVG",
    "6. Linking the bars to the scan",
    "7. Editing the MEI file live",
    "8. Wrap-up",
    "Notebooks",
    "Sources",
]


class LinkTargets(HTMLParser):
    """Read links and element ids without executing a target page's demos."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.links = set()
        self.ids = set()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id") is not None:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href") is not None:
            self.links.add(attrs["href"])

    handle_startendtag = handle_starttag


def check_same_site_links(request, source_url, tag):
    """Check all local anchor links, including downloads and fragment targets."""
    source = request.get(source_url)
    expect(source.status == 200, f"{tag}: HTTP {source.status} for {source_url}")
    if source.status != 200:
        return
    source_doc = LinkTargets(source.text())
    targets = {source_url: (source.status, source_doc.ids)}
    origin = urlsplit(URL)
    checked = 0
    for href in sorted(source_doc.links):
        target, fragment = urldefrag(urljoin(source_url, href))
        parsed = urlsplit(target)
        if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc):
            continue
        checked += 1
        if target not in targets:
            try:
                response = request.get(target)
                ids = (LinkTargets(response.text()).ids
                       if "text/html" in response.headers.get("content-type", "") else set())
                targets[target] = (response.status, ids)
                response.dispose()
            except Exception as exc:
                expect(False, f"{tag}: link {href}: {exc}")
                continue
        status, ids = targets[target]
        expect(status == 200, f"{tag}: link {href}: HTTP {status}")
        if fragment and status == 200:
            expect(unquote(fragment) in ids, f"{tag}: link {href}: missing id {unquote(fragment)!r}")
    source.dispose()
    print(f"{tag}: checked {checked} same-site links")


def check_session_page(b, width, height):
    logs = []
    ctx = b.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"[:200]) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"[:300]))
    tag = f"session page {width}"
    print(f"== {tag}")
    response = page.goto(URL)
    expect(response is not None and response.status == 200, f"{tag}: page found")
    headings = page.locator("article h2").evaluate_all("""hs => hs.map(h => {
        const text = h.cloneNode(true);
        text.querySelectorAll('.headerlink').forEach(a => a.remove());
        return text.textContent.trim();
    })""")
    expect(headings == HEADINGS, f"{tag}: h2 headings {headings}")
    expect(page.locator("[data-demo]").count() == 0, f"{tag}: no data-demo elements")
    page.screenshot(path=f"{OUT}/session_{width}.png", full_page=True)
    sw, cw = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    expect(sw <= cw, f"{tag}: page overflow {sw} > {cw}")
    errors = [line for line in logs if not line.startswith("warning")]
    expect(not errors, f"{tag}: console {errors}")
    print("console:", logs)
    ctx.close()


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
    request = p.request.new_context()
    for url, tag in [(URL, "session page"), (URL + "svg/", "svg page")]:
        check_same_site_links(request, url, tag)
    request.dispose()
    for width, height in [(1280, 900), (390, 844)]:
        check_session_page(b, width, height)
        for scheme in ("light", "dark"):
            check_svg_page(b, width, height, scheme)
    b.close()
server.shutdown()
server.server_close()
print("screenshots:", OUT)
print(f"session and svg pages: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
