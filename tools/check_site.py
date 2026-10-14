"""Drive the session-1 demos in headless Chromium and print what they show.

Usage (from the repository root):
    .venv/bin/mkdocs build -d site
    .venv/bin/python tools/check_site.py [screenshot_dir]

Needs `pip install playwright` and `playwright install chromium`. The roll
demo fetches the SUPRA MIDI files from GitHub and the facsimile demo loads
the scan from the BSB IIIF server, so both need network access.
Expected on 2026-10-14: 11 notes in each of the six formats, 5 GABC neumes,
grid round trip 5/11 then 11/11 with onsets, both recorded LLM answers all
ticks, 15 zones, bars and hit areas in Demo E (zone 11 selects bar rfwucfq
with its editorial note; render bar 5 selects zone 4), 6,031 notes
(expressive) and 33,508 holes (raw), no console errors.
"""

import functools
import http.server
import json
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "site"
OUT = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="check_site_")
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{server.server_address[1]}/sessions/01-why-encode-music/"
logs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1000, "height": 900})
    page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"[:200]) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"[:300]))
    page.goto(URL)
    # Demo B
    page.wait_for_function("document.querySelectorAll('[data-demo=formats] .vrv-score svg').length >= 7", timeout=90000)
    cards = page.eval_on_selector_all("[data-demo=formats] .vrv-card", """cs => cs.map(c => ({
        name: c.querySelector('header strong').textContent,
        size: c.querySelector('.vrv-size').textContent,
        notes: c.querySelectorAll('.vrv-score g.note, .vrv-score g.nc').length,
        msgs: [...c.querySelectorAll('.vrv-messages li')].map(l => l.className + ': ' + l.textContent).join(' | ').slice(0, 160)}))""")
    for c in cards: print("B", c)
    # B: piano roll + MEI buttons on kern card, then a crash input in ABC
    kern = page.locator("[data-demo=formats] .vrv-card").nth(1)
    kern.get_by_role("button", name="Piano roll").click()
    kern.get_by_role("button", name="Show as MEI").click()
    print("B kern MEI chars:", len(kern.locator("pre.vrv-mei").text_content()))
    kern.screenshot(path=f"{OUT}/b_kern.png")
    abc = page.locator("[data-demo=formats] .vrv-card").nth(0)
    abc.locator("textarea").fill("X:1\nK:C\nCD]EF|\n")
    page.wait_for_timeout(1500)
    print("B abc broken:", abc.locator(".vrv-messages").text_content()[:200])
    abc.locator("textarea").fill("X:1\nT:t\nM:3/4\nL:1/4\nK:G\nG A B | c2 ^F | G3 |]\n")
    page.wait_for_timeout(1500)
    print("B abc edited notes:", abc.locator(".vrv-score g.note").count())
    # Demo C
    page.wait_for_selector("[data-demo=grid] table.grid-table", timeout=30000)
    grid = page.locator("[data-demo=grid]")
    print("C summary:", grid.locator(".grid-summary").text_content())
    print("C text:\n" + grid.locator("pre.grid-text").text_content())
    grid.get_by_label("keep an onset grid").check()
    page.wait_for_timeout(1000)
    print("C onset summary:", grid.locator(".grid-summary").text_content())
    grid.screenshot(path=f"{OUT}/c_grid.png")
    grid.locator("select").select_option("2")
    page.wait_for_timeout(800)
    print("C eighth cols:", grid.locator("table.grid-table tbody tr").first.locator("td").count())
    # Demo D
    llm = page.locator("[data-demo=llm]")
    for label in ["Claude Opus 5.5 · ABC", "Claude Opus 5.5 · kern", "Constructed example with typical errors"]:
        llm.get_by_role("button", name=label).click()
        page.wait_for_selector("[data-demo=llm] table.llm-checks", timeout=30000)
        page.wait_for_timeout(1200)
        rows = llm.locator("table.llm-checks tr").all_text_contents()
        print("D", label, "::", " || ".join(r.replace("\n", " ") for r in rows))
    llm.screenshot(path=f"{OUT}/d_llm.png")
    # Demo E
    page.wait_for_selector("[data-demo=facsimile] rect.facs-hit", timeout=60000)
    fac = page.locator("[data-demo=facsimile]")
    print("E zones:", fac.locator("rect.facs-zone").count(), "bars:", fac.locator(".facs-render g.measure").count(),
          "hit areas:", fac.locator("rect.facs-hit").count())
    fac.locator("rect.facs-zone").nth(10).click(force=True)
    page.wait_for_function("(i => i.complete && i.naturalWidth > 0)(document.querySelector('[data-demo=facsimile] .facs-crop'))", timeout=30000)
    print("E zone 11:", fac.locator(".facs-detail strong").first.text_content(), "| render bar:",
          fac.locator(".facs-render g.measure.is-active").get_attribute("id"), "| note:", fac.locator(".facs-notes").text_content()[:80])
    fac.screenshot(path=f"{OUT}/e_facsimile.png")
    fac.locator(".facs-render g.measure").nth(4).locator("rect.facs-hit").click(force=True)
    print("E render bar 5 -> zone", fac.locator("rect.facs-zone.is-active").get_attribute("data-i"))
    # Demo A
    roll = page.locator("[data-demo=roll]")
    roll.get_by_role("button").click()
    page.wait_for_selector("[data-demo=roll] canvas", timeout=60000)
    page.wait_for_timeout(500)
    print("A info:", roll.locator("p.vrv-note").text_content())
    roll.screenshot(path=f"{OUT}/a_exp.png")
    roll.locator("select").first.select_option("raw")
    page.wait_for_timeout(300)
    print("A info raw:", roll.locator("p.vrv-note").text_content())
    roll.screenshot(path=f"{OUT}/a_raw.png")
    b.close()
server.shutdown()
print("screenshots:", OUT)
print("console:", json.dumps(logs, indent=0)[:1500])
