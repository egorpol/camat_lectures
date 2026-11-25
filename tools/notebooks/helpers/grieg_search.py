"""Grieg's Vöglein, session 4 block 2: search for the bird call and publish a finding.

Pasted after grieg_linking.py, grieg_editing.py, grieg_publish.py and grieg_analysis.py
in the same cell. It uses their names for reading the score, showing the scan, and
checking the edition. Helpers must not import each other.
"""

from bisect import bisect_left, bisect_right
from contextlib import redirect_stdout
from http.client import HTTPException
from numbers import Integral
from xml.parsers import expat
from xml.sax.saxutils import escape, quoteattr

FINDING_ID = "seminar-finding"
FINDING_CATEGORIES = ("repeat", "sequence-step", "false-hit")
FINDING_PLACEHOLDER = "Replace this with one sentence about what you see in the score and scan."
SEARCH_COLUMNS = ["hit", "score", "semitones", "bars", "matched notes", "cells", "note IDs"]
SEARCH_COLOUR = "#b32057"


def open_search_folder(start=None):
    """Find the pair's session-3 edition without preparing any other folder."""
    start = Path(start or Path.cwd()).resolve()
    candidates = [
        start / "grieg_edition_work",
        (start / "../03-linking-and-editing/grieg_edition_work").resolve(),
        (start / "../../03-linking-and-editing/notebooks/grieg_edition_work").resolve(),
        start / "sessions/03-linking-and-editing/notebooks/grieg_edition_work",
    ]
    for project in candidates:
        edition = project / "edition"
        work = edition / "mei/work.mei"
        try:
            if not (_class_folder_ok(project) and work.is_file()):
                continue
            root = _read(work)
            if root is None:
                return
            if root.find(f".//{{{MEI_NS}}}facsimile") is None:
                continue
            inputs = project / "inputs"
            settings = json.loads((inputs / "settings.json").read_text(encoding="utf-8"))
            mei = inputs / settings["mei"]
            source = _read(mei)
            if source is None:
                return
            layout = _layout_systems(settings["layout"])
        except (OSError, ValueError, KeyError, TypeError):
            print("✗ The session-3 files could not be opened. Run 03_grieg_linking.ipynb "
                  "in your session-3 folder, then try again.")
            return
        print("✓ Found your session-3 edition in", project)
        if not notes_equal(source, root)[0]:
            print("! Your notes differ from the source. Hit numbers may differ from the instructor's sheet, "
                  "so check each hit by its bars.")
        return {
            "project": project, "inputs": inputs, "settings": settings, "mei": mei,
            "before": edition / "checkpoints/before-editing.mei", "work": work,
            "edition": edition, "pages_json": edition / "pages/pages.json", "layout_systems": layout,
        }
    print("✗ Your linked work.mei is missing. Run 03_grieg_linking.ipynb to the end "
          "in your session-3 folder, then run this cell again.")


def _search_grid(context, chroma=False):
    from camat import parse_files
    from camat.binary_roundtrip import prepare_binary_timeline
    from camat.music_utils import create_binary_matrix_bundle

    if context is None:
        return
    path = context["work"]
    try:
        data = path.read_bytes()
        cached = context.get("search_grid")
        if cached is None or cached["data"] != data:
            root = ET.fromstring(data)
            with redirect_stdout(io.StringIO()):
                scores, _, _ = parse_files(
                    [str(path)], backend="none", include_xml_ids=True, quiet_native_warnings=True,
                    display_preview_df_pitch=False, display_preview_df_events=False,
                )
            if not scores:
                raise ValueError("no score")
            score = scores[0]
            notes, offsets, origin = prepare_binary_timeline(score["df_pitch"], score["measure_offsets"])
            call = notes[notes["Source Global Onset"].between(-0.5, 0.5, inclusive="left")].copy()
            call["Global Onset"] = call["Source Global Onset"] + 0.5
            bars = [bar for bar, _ in _music_measure_list(root)]
            if call.empty or len(bars) != len(offsets):
                raise ValueError("missing call or bar positions")
            order = {note.get(XML_ID): i for i, note in enumerate(
                root.find(f"{{{MEI_NS}}}music").iter(f"{{{MEI_NS}}}note")
            ) if note.get(XML_ID)}
            cached = context["search_grid"] = {
                "data": data, "notes": notes, "offsets": offsets, "origin": origin,
                "call": call, "bars": bars, "order": order, "bundles": {},
            }
        mode = "chroma" if chroma else "minmax"
        if mode not in cached["bundles"]:
            grid = dict(y_mode=mode, resolution_method="manual", manual_resolution=0.125,
                        row_order="high_to_low", include_provenance=True)
            host = create_binary_matrix_bundle(cached["notes"], measure_offsets=cached["offsets"], **grid)
            host.meta["source_time_origin"] = cached["origin"]
            query = create_binary_matrix_bundle(cached["call"], **grid)
            cached["bundles"][mode] = host, query
        return cached, *cached["bundles"][mode]
    except (OSError, ET.ParseError, ValueError, KeyError, RuntimeError):
        print("✗ CAMAT could not read the notes and bars in work.mei. "
              "Check that it opens in your edition, then run this cell again.")


def _search_note_ids(cached, notes):
    order = cached["order"]
    return tuple(sorted({i for i in notes.get("xml_id", ()) if i in order}, key=order.__getitem__))


def _search_bar_range(bars):
    return bars[0] if len(bars) == 1 else f"{bars[0]}–{bars[-1]}"


def _search_bar_label(bars):
    return f"{'bars' if '–' in bars else 'bar'} {bars}"


def _search_shift(semitones, chroma=False):
    if chroma:
        return f"pitch classes shifted by {semitones} semitones"
    if semitones == 0:
        return "at the printed pitch"
    amount = abs(semitones)
    unit = "semitone" if amount == 1 else "semitones"
    return f"{amount} {unit} {'higher' if semitones > 0 else 'lower'} than bar 1"


def search(context, every_pitch=True, chroma=False, min_score=0.75):
    """Show and return the numbered hits, keeping the matched IDs out of the display."""
    from camat.binary_query import search_binary_query
    from camat.binary_roundtrip import binary_match_sources

    grid = _search_grid(context, chroma)
    rows = []
    if grid is not None:
        cached, host, query = grid
        try:
            result = search_binary_query(
                host, query, transpositions="all" if every_pitch or chroma else [0],
                top_n=None, min_score=min_score, max_time_iou=0.5,
            )
        except (ValueError, TypeError):
            print("✗ The search could not run. Try the starting score limit of 0.75.")
            return pd.DataFrame(columns=SEARCH_COLUMNS)
        matches = result["matches"].sort_values(
            ["score", "source_onset_QL", "transpose_semitones"], ascending=[False, True, True]
        )
        filled = int(query.matrix.sum())
        offsets = cached["offsets"]
        for number, hit in enumerate(matches.itertuples(index=False), 1):
            kernel = result["variants"][hit.time_scale, hit.transpose_semitones]["kernel"]
            sources = binary_match_sources(host, kernel, hit.row, hit.col)
            start = bisect_right(offsets, hit.grid_onset_QL) - 1
            stop = bisect_left(offsets, hit.grid_end_QL)
            bars = cached["bars"][start:stop]
            matched = sources["matched_notes"]
            rows.append((number, float(hit.score), int(hit.transpose_semitones), _search_bar_range(bars),
                         f"{len(matched)} of {len(sources['window_notes'])}",
                         f"{filled - len(sources['missing_cells'])} of {filled}",
                         _search_note_ids(cached, matched)))
    hits = pd.DataFrame(rows, columns=SEARCH_COLUMNS)
    hits.attrs["chroma"] = chroma
    if grid is not None:
        hits.attrs["searched_mei"] = cached["data"]
        if hits.empty:
            print("! No hits at this score limit. Try a lower number.")
        else:
            print(f"✓ {len(hits)} hits.")
            table = hits.drop(columns="note IDs").to_html(
                index=False, formatters={"score": lambda value: str(round(value, 6))}
            )
            display(HTML(table))
    return hits


def _search_read_work(context):
    try:
        return _read(context["work"])
    except OSError:
        print("✗ work.mei could not be opened. Check your session-3 folder and run setup again.")


def _search_notes_current(hits, root):
    searched_mei = hits.attrs.get("searched_mei")
    if searched_mei is not None and notes_equal(ET.fromstring(searched_mei), root)[0]:
        return True
    print("! work.mei has changed since the search. Run the search cells again.")
    return False


def _show_search_score(root, bars, ids):
    import verovio

    excerpt = _excerpt_measures(root, bars)
    music = excerpt.find(f"{{{MEI_NS}}}music")
    for note in music.iter(f"{{{MEI_NS}}}note"):
        if note.get(XML_ID) in ids:
            note.set("color", SEARCH_COLOUR)
    verovio.enableLog(False)
    try:
        tk = verovio.toolkit()
        tk.setOptions({"breaks": "none", "header": "none", "footer": "none", "mnumInterval": 1,
                       "scale": 40, "pageWidth": 1800, "adjustPageHeight": True})
        if tk.loadData(ET.tostring(excerpt, encoding="unicode")):
            display(HTML(tk.renderToSVG(1)))
        else:
            print("✗ The score could not be drawn. Check that work.mei opens in your edition.")
    except RuntimeError:
        print("✗ The score could not be drawn. Check that work.mei opens in your edition.")


def _show_search_scan(context, bars):
    try:
        boxes = _boxes(context)
        if any(bar not in boxes for bar in bars):
            print("! Some bars have no box on the scan. Check the links in 03_grieg_linking.ipynb.")
        for _, _, system in context["layout_systems"]:
            kept = [bar for bar in system if bar in bars and bar in boxes]
            if not kept:
                continue
            image = boxes[kept[0]][0]
            rects = [boxes[bar][1] for bar in kept]
            left, top = (min(rect[i] for rect in rects) for i in (0, 1))
            right, bottom = (max(rect[i] for rect in rects) for i in (2, 3))
            labels = [(boxes[bar][1][0] + 30, top + 10, f"bar {bar}") for bar in kept]
            _crop(image, (left, top, right, bottom), labels)
    except (OSError, ET.ParseError, KeyError, ValueError, AttributeError):
        print("✗ The scan could not be opened. Check the pages and links in 03_grieg_linking.ipynb.")


def show_query(context):
    """Show the pickup and its landing on the score, the scan and the grid."""
    import matplotlib.pyplot as plt

    grid = _search_grid(context)
    if grid is None:
        return
    cached, _, query = grid
    root = _search_read_work(context)
    if root is None:
        return
    call = cached["call"]
    ids = _search_note_ids(cached, call)
    bars = [str(bar) for bar in call["Measure"].unique()]
    _show_search_score(root, bars, ids)
    _show_search_scan(context, bars)
    fig, ax = plt.subplots(figsize=(3, 3))
    height, width = query.matrix.shape
    ax.imshow(query.matrix, cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
    ax.set(xticks=[], yticks=[], xlabel="Time →", ylabel="Pitch → higher")
    ax.set_xticks([i - 0.5 for i in range(width + 1)], minor=True)
    ax.set_yticks([i - 0.5 for i in range(height + 1)], minor=True)
    ax.grid(which="minor", color="#cccccc", linewidth=0.5)
    ax.tick_params(which="minor", length=0)
    fig.tight_layout()
    plt.show()
    plt.close(fig)
    print(f"✓ {len(call)} notes, {int(query.matrix.sum())} filled cells, "
          "from bar 1 to the landing note in bar 2.")


def _search_hit(hits, number):
    if hits is None or hits.empty:
        print("! Run the search first so there are hits to choose from.")
        return
    if isinstance(number, Integral) and not isinstance(number, bool):
        row = hits[hits["hit"] == number]
        if not row.empty:
            return row.iloc[0]
    print(f"! There is no hit {number}. Choose a number from 1 to {len(hits)}.")


def _search_counts(hit):
    matched, window = hit["matched notes"].split(" of ")
    filled, total = hit["cells"].split(" of ")
    return matched, window, filled, total


def show_hits(context, hits, numbers):
    """Show each chosen hit in the score and on the scan."""
    if context is None:
        return
    root = _search_read_work(context)
    if root is None:
        return
    if hits is not None and not hits.empty and not _search_notes_current(hits, root):
        return
    if not pd.api.types.is_list_like(numbers):
        numbers = [numbers]
    for number in numbers:
        hit = _search_hit(hits, number)
        if hit is None:
            continue
        shift = _search_shift(hit["semitones"], hits.attrs.get("chroma", False))
        print(f"Hit {number} · score {hit['score']} · {shift} · {_search_bar_label(hit['bars'])}")
        matched, window, filled, total = _search_counts(hit)
        if len(hit["note IDs"]) != int(matched):
            print("! Some matched notes have no xml:id in work.mei, so they will not be highlighted.")
        first, *last = hit["bars"].split("–")
        bars = [str(bar) for bar in range(int(first), int(last[0] if last else first) + 1)]
        _show_search_score(root, bars, hit["note IDs"])
        _show_search_scan(context, bars)
        print(f"{filled} of the {total} cells of the call are filled here; "
              f"{matched} of the {window} notes in this stretch match.")


def _finding_draft(hit, chroma):
    shift = _search_shift(hit["semitones"], chroma)
    matched, window, filled, total = _search_counts(hit)
    return (f"Bird-call search (CAMAT 0.2.8), hit {hit['hit']}: {_search_bar_label(hit['bars'])}, {shift}; "
            f"{filled} of the {total} cells of the call are filled, {matched} of the {window} notes match.")


def draft_finding(hits, number):
    """Print and return the search facts for this hit."""
    hit = _search_hit(hits, number)
    if hit is not None:
        draft = _finding_draft(hit, hits.attrs.get("chroma", False))
        print(draft)
        return draft


def _finding_positions(data, wanted):
    """Find the opening and closing tag bytes for elements with the given IDs."""
    parser = expat.ParserCreate(namespace_separator="}")
    stack = []
    spans = {}

    def start(_tag, attributes):
        xml_id = attributes.get(XML_ID[1:])
        stack.append((xml_id, parser.CurrentByteIndex))

    def end(_tag):
        xml_id, opening = stack.pop()
        if xml_id in wanted:
            spans[xml_id] = opening, parser.CurrentByteIndex

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.Parse(data, True)
    return spans


def _finding_block(indent, newline, label, plist, paragraphs):
    entities = {'"': "&quot;", "'": "&apos;", "\n": "&#10;", "\r": "&#13;"}
    lines = [f'{indent}<annot xml:id="{FINDING_ID}" type="finding" '
             f'label={quoteattr(label)} plist={quoteattr(plist)}>']
    lines.extend(f"{indent}  <p>{escape(text, entities)}</p>" for text in paragraphs)
    lines.append(f"{indent}</annot>")
    return (newline.join(lines) + newline).encode("utf-8")


def _finding_signature(annot):
    return (
        annot.get("label"), annot.get("plist"),
        tuple("".join(p.itertext()) for p in annot.findall(f"{{{MEI_NS}}}p")),
    )


def _old_finding_block(data, old, span):
    opening, closing = span
    start = data.rfind(b"\n", 0, opening) + 1
    end = re.match(rb"</annot>(\r?\n)", data[closing:])
    indent = data[start:opening]
    problem = ("Delete the old seminar-finding by hand in work.mei, save, and run this cell again.")
    if end is None or indent.strip(b" \t") or old.get("type") != "finding":
        raise ValueError(problem)
    label, plist, paragraphs = _finding_signature(old)
    if label not in FINDING_CATEGORIES or not plist or len(paragraphs) != 2:
        raise ValueError(problem)
    expected = _finding_block(indent.decode(), end[1].decode(), label, plist, paragraphs)
    actual = data[start:closing + end.end()]
    if actual != expected or data.count(expected) != 1:
        raise ValueError(problem)
    return start, actual


def _finding_line_changes(before, after, old_line, new_line):
    """Every edited line must belong to the old or new four-line finding."""
    diff = difflib.SequenceMatcher(None, before.splitlines(keepends=True),
                                   after.splitlines(keepends=True), autojunk=False)
    return all(
        kind == "equal"
        or ((a == b or old_line is not None and old_line <= a <= b <= old_line + 4)
            and (c == d or new_line <= c <= d <= new_line + 4))
        for kind, a, b, c, d in diff.get_opcodes()
    )


def _insert_finding(data, old_root, hit_ids, label, paragraphs):
    notes = {note.get(XML_ID): measure for _, measure in _music_measure_list(old_root)
             for note in measure.iter(f"{{{MEI_NS}}}note") if note.get(XML_ID)}
    matched = [note_id for note_id in notes if note_id in hit_ids]
    if not matched or len(matched) != len(hit_ids):
        raise ValueError("The matched notes could not be found in work.mei. Run the search again.")
    measure = notes[matched[0]]
    measure_id = measure.get(XML_ID)
    if not measure_id:
        raise ValueError("The first matched bar has no ID in work.mei. Ask your instructor to check it.")
    ids, duplicates = _all_ids(old_root)
    if FINDING_ID in duplicates:
        raise ValueError("Delete the old seminar-finding entries by hand, save, and run this cell again.")
    old = ids.get(FINDING_ID)
    if old is not None and old.tag != f"{{{MEI_NS}}}annot":
        raise ValueError("The name seminar-finding is already in use. Ask your instructor to check work.mei.")

    positions = _finding_positions(data, {measure_id, FINDING_ID})
    opening, closing = positions[measure_id]
    insertion = data.rfind(b"\n", 0, closing) + 1
    indent = data[data.rfind(b"\n", 0, opening) + 1:opening]
    line_end = re.match(rb"</measure>[ \t]*(\r?\n)", data[closing:])
    if indent.strip(b" \t") or data[insertion:closing].strip(b" \t") or line_end is None:
        raise ValueError("The first matched bar needs its opening and closing tags on their own lines. "
                         "Ask your instructor to check work.mei.")
    plist = " ".join(f"#{note_id}" for note_id in matched)
    block = _finding_block(indent.decode() + "  ", line_end[1].decode(), label, plist, paragraphs)
    clean = data
    old_line = None
    if old is not None:
        start, previous = _old_finding_block(data, old, positions[FINDING_ID])
        old_line = data.count(b"\n", 0, start)
        clean = data[:start] + data[start + len(previous):]
        if start < insertion:
            insertion -= len(previous)

    updated = clean[:insertion] + block + clean[insertion:]
    new_root = ET.fromstring(updated)
    new_ids, duplicates = _all_ids(new_root)
    found = new_ids.get(FINDING_ID)
    new_measure = new_ids.get(measure_id)
    if (duplicates or found is None or new_measure is None or not len(new_measure)
            or new_measure[-1] is not found or _finding_signature(found) != (label, plist, paragraphs)):
        raise ValueError("The new finding did not pass the ID and placement checks. Ask your instructor to check work.mei.")
    if any(target.lstrip("#") not in new_ids
           for element in new_root.iter() for target in element.get("plist", "").split()):
        raise ValueError("A note link in work.mei points to an ID that is missing. Ask your instructor to check it.")
    if not notes_equal(old_root, new_root)[0]:
        raise ValueError("The note check found a difference. Ask your instructor to check work.mei.")
    if not _finding_line_changes(data, updated, old_line, clean.count(b"\n", 0, insertion)):
        raise ValueError("The edit would touch lines outside the finding. Ask your instructor to check work.mei.")
    return updated, block


def _save_search_text(path, updated):
    text = updated.decode("utf-8")
    native = text.replace(os.linesep, "\n")
    if native.replace("\n", os.linesep) == text:
        _replace(path, native)
        return
    # On Windows the shared text writer translates LF. Keep LF or mixed endings byte-for-byte.
    with tempfile.TemporaryDirectory(dir=path.parent) as folder:
        saved = Path(folder) / path.name
        saved.write_bytes(updated)
        os.replace(saved, path)


def write_finding(context, hits, number, category, sentence):
    """Put the pair's finding in work.mei and build a local test copy of the page."""
    from camat.web_edition import SiteConfigError, build_site

    if context is None:
        return
    hit = _search_hit(hits, number)
    if hit is None:
        return
    if category not in FINDING_CATEGORIES:
        print("! Choose repeat, sequence-step or false-hit for MY_CATEGORY.")
        return
    if not isinstance(sentence, str) or sentence.strip() in ("", FINDING_PLACEHOLDER):
        print("! Write your own sentence in MY_SENTENCE about what you see in the score and scan.")
        return
    config = context["edition"] / "site.json"
    if not config.is_file():
        print("✗ site.json is missing. Run 03_grieg_live_page.ipynb first, then run this cell again.")
        return
    path = context["work"]
    paragraphs = (_finding_draft(hit, hits.attrs.get("chroma", False)), sentence)
    try:
        data = path.read_bytes()
        root = ET.fromstring(data)
        if not _search_notes_current(hits, root):
            return
        if len(hit["note IDs"]) != int(_search_counts(hit)[0]):
            print("✗ Some matched notes have no xml:id in work.mei, so the finding could not link them. "
                  "Ask your instructor to check work.mei. No change to work.mei.")
            return
        updated, block = _insert_finding(data, root, hit["note IDs"], category, paragraphs)
        if path.read_bytes() != data:
            raise ValueError("work.mei changed while the finding was being prepared. Run this cell again.")
        if updated != data:
            _save_search_text(path, updated)
    except ValueError as error:
        print(f"✗ {error} No change to work.mei.")
        return
    except (OSError, ET.ParseError, expat.ExpatError):
        print("✗ The finding could not be saved. Check that work.mei opens and that you can save it.")
        return

    cached = context.get("search_grid")
    if cached is not None and cached["data"] == data:
        cached["data"] = updated
    count = len(hit["note IDs"])
    print(f"✓ work.mei: 1 finding, {category.replace('-', ' ')}, {_search_bar_label(hit['bars'])} ({count} notes)")
    print(block.decode("utf-8").rstrip("\r\n"))
    try:
        with tempfile.TemporaryDirectory() as folder:
            report = build_site(config, Path(folder) / "_site")
    except SiteConfigError as error:
        print("✗ The finding is saved. The test page could not be built. Check the messages below before syncing.")
        for problem in error.problems:
            print(" ", problem)
        return
    except OSError:
        print("✗ The finding is saved. The test page could not be built. Check your edition folder and try again.")
        return
    work = report["works"][0]
    unit = "entry" if work["notes"] == 1 else "entries"
    print(f"✓ test build: {work['measures']} bars, {work['notes']} {unit} under Editorial notes; GitHub builds the same")
    return report


def _live_score_finding(root):
    music = root.find(f"{{{MEI_NS}}}music")
    if music is None:
        return
    found = [annot for annot in music.iter(f"{{{MEI_NS}}}annot") if annot.get(XML_ID) == FINDING_ID]
    if len(found) == 1:
        return found[0]


def check_live_finding(context):
    """Compare the published finding with the one in the pair's local edition."""
    github = context.get("github") if context else None
    if not github:
        print("! Run the repository check first.")
        return
    root = _search_read_work(context)
    if root is None:
        return
    local = _live_score_finding(root)
    if local is None:
        print("! Write a finding in work.mei first, then commit and sync it.")
        return
    owner, repo = github["owner"], github["repo"]
    url = f"https://{owner.lower()}.github.io/{repo}/"
    try:
        data, problem = _fetch_bytes(url + "mei/work.mei")
    except (OSError, HTTPException):
        data, problem = None, "no connection"
    if problem == "no connection":
        print("✗ The live page could not be reached. Check your internet connection and run this cell again.")
        return
    if problem:
        print(f"! The score is not online yet at {url}. Look at Actions on GitHub and try again.")
        return
    try:
        remote = _live_score_finding(ET.fromstring(data))
    except ET.ParseError:
        remote = None
    if remote is None or _finding_signature(local) != _finding_signature(remote):
        print("! The live page still has an older copy or no finding. Wait a minute, reload with Ctrl+Shift+R "
              "or Cmd+Shift+R on a Mac, and look at Actions on GitHub.")
        return
    targets = (local.get("plist") or "").split()
    if targets:
        first = targets[0].lstrip("#")
        for bar, measure in _music_measure_list(root):
            if any(note.get(XML_ID) == first for note in measure.iter(f"{{{MEI_NS}}}note")):
                print(f"✓ Your finding is online. Click it under Editorial notes at {url}#{WORK_ID}/{bar}")
                return
    print(f"✓ Your finding is online. Click it under Editorial notes at {url}")
