"""Offline tests for the session 4 bird-call search and finding."""

import difflib
import hashlib
import io
import shutil
import subprocess
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from http.client import IncompleteRead
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HELPERS = Path(__file__).resolve().parent / "helpers"
SESSION_3 = ROOT / "sessions/03-linking-and-editing/notebooks/grieg_edition_work"
REFERENCE = ROOT / "sessions/04-publishing-and-analysis/fixtures/grieg-voglein-test-83eed567f"
# Both inputs stay local: the reference fixture and an in-place run of the session 3 notebooks.
# Tests that copy them skip without them; the others also run on a fresh clone.
LOCAL_INPUTS = [REFERENCE / "mei/work.mei", REFERENCE / "site.json"] + [SESSION_3 / rel for rel in (
    "inputs/settings.json", "inputs/Grieg_Little_bird_Op43_No4.mei", "edition/checkpoints/before-editing.mei",
    "edition/pages/pages.json", "edition/pages/page-0001.png", "edition/pages/page-0002.png")]
MEI ="{http://www.music-encoding.org/ns/mei}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
NOTE_IDS = {
    1: ("d418889e30 d418889e55 d418889e77 d418889e97 d418889e139 d418889e159 "
        "d418889e179 d418889e199 d418889e221 d418889e346").split(),
    8: "d418889e378 d418889e394 d418889e409 d418889e426".split(),
    10: "d418889e265 d418889e305 d418889e444 d418889e486 d418889e528 d418889e657".split(),
}
DRAFT_10 = ("Bird-call search (CAMAT 0.2.8), hit 10: bars 2–3, 5 semitones higher than bar 1; "
            "12 of the 16 cells of the call are filled, 6 of the 8 notes match.")
SENTENCE = "The short notes keep the call's rhythm while some intervals change."
PLACEHOLDER = "Replace this with one sentence about what you see in the score and scan."
# The tests check how a label is saved, not which label a hit should get: every write below
# writes each label in turn to the same hit, so no test pairs a hit with one label.
LABELS = ("repeat", "sequence-step", "false-hit")


@pytest.fixture(scope="module")
def H():
    names = ("grieg_linking", "grieg_editing", "grieg_publish", "grieg_analysis", "grieg_search")
    code = "\n\n".join((HELPERS / f"{name}.py").read_text(encoding="utf-8") for name in names)
    namespace = {"__name__": "grieg_search_test"}
    exec(compile(code, "grieg_search_helpers", "exec"), namespace)
    return namespace


def _copy_edition(folder):
    missing = [path for path in LOCAL_INPUTS if not path.is_file()]
    if missing:
        pytest.skip(f"needs {len(missing)} local input file(s), such as {missing[0].relative_to(ROOT)}")
    project = folder / "grieg_edition_work"
    # Leave out a class_edition/ that a class run of block 1 may have left in the session 3 folder.
    shutil.copytree(SESSION_3, project,
                    ignore=lambda folder, names: ["class_edition"] if Path(folder) == SESSION_3 else [])
    (project / "edition/mei").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REFERENCE / "mei/work.mei", project / "edition/mei/work.mei")
    shutil.copyfile(REFERENCE / "site.json", project / "edition/site.json")
    return project


def _write_each_label(H, context, hits, number, sentence=SENTENCE):
    """Write each label in turn to one hit (each write replaces the last); return the reports."""
    return [H["write_finding"](context, hits, number, label, sentence) for label in LABELS]


@pytest.fixture(scope="module", autouse=True)
def offline():
    original = urllib.request.urlopen

    def no_network(request, *args, **kwargs):
        url = request.full_url if isinstance(request, urllib.request.Request) else request
        if url.startswith("file:"):
            return original(request, *args, **kwargs)
        pytest.fail("An offline test tried to open the network.")

    with pytest.MonkeyPatch.context() as network:
        network.setattr(urllib.request, "urlopen", no_network)
        yield


@pytest.fixture(scope="module")
def reference(H, tmp_path_factory):
    project = _copy_edition(tmp_path_factory.mktemp("reference"))
    context = H["open_search_folder"](project.parent)
    return context, H["search"](context)


@pytest.fixture
def edition(H, tmp_path):
    project = _copy_edition(tmp_path)
    return H["open_search_folder"](project.parent)


def _measures(root):
    return {measure.attrib["n"]: measure for measure in root.find(f"{MEI}music").iter(f"{MEI}measure")}


def _finding(root):
    return [el for el in root.iter(f"{MEI}annot") if el.get(XML_ID) == "seminar-finding"]


def _notes(root):
    return [ET.tostring(note) for measure in _measures(root).values() for note in measure.iter(f"{MEI}note")]


def _expect_only_added_finding(before, after, bar):
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    assert before_lines[:3] == after_lines[:3], "The XML declaration and both xml-model lines must be byte-identical"
    assert sum(line.startswith(b"<?xml-model ") for line in before_lines[:3]) == 2
    changes = [op for op in difflib.SequenceMatcher(None, before_lines, after_lines, autojunk=False).get_opcodes()
               if op[0] != "equal"]
    [(action, i, j, k, end)] = changes
    assert action == "insert" and i == j and end - k == 4
    assert before_lines[i].strip() == b"</measure>"
    start = next(line for line in reversed(before_lines[:i]) if b"<measure " in line)
    assert f'n="{bar}"'.encode() in start and b'xml:id="' in start
    indent = start[:len(start) - len(start.lstrip())] + b"  "
    assert after_lines[k].startswith(indent + b"<annot ")
    assert b'<annot xml:id="seminar-finding"' in after_lines[k]
    assert after_lines[end - 1].strip() == b"</annot>"
    assert b"".join(after_lines[:k] + after_lines[end:]) == before


def test_hits_at_every_pitch(reference):
    _, hits = reference
    expected = [
        (1.0, 0, "1–2", "10 of 10", "16 of 16"),
        (1.0, 0, "3–4", "10 of 10", "16 of 16"),
        (1.0, 0, "4–5", "10 of 10", "16 of 16"),
        (1.0, 7, "6–7", "10 of 10", "16 of 16"),
        (1.0, 0, "22–23", "10 of 10", "16 of 16"),
        (1.0, 0, "25–26", "10 of 10", "16 of 16"),
        (0.875, 0, "24–25", "8 of 9", "14 of 16"),
        (0.75, -12, "2", "4 of 4", "12 of 16"),
        (0.75, -12, "2", "4 of 4", "12 of 16"),
        (0.75, 5, "2–3", "6 of 8", "12 of 16"),
        (0.75, -7, "3", "4 of 4", "12 of 16"),
        (0.75, -7, "3", "4 of 4", "12 of 16"),
        (0.75, -4, "4", "6 of 8", "12 of 16"),
        (0.75, -12, "5", "4 of 4", "12 of 16"),
        (0.75, -12, "5", "4 of 4", "12 of 16"),
        (0.75, 3, "5–6", "6 of 8", "12 of 16"),
        (0.75, -9, "6", "4 of 4", "12 of 16"),
        (0.75, -9, "6", "4 of 4", "12 of 16"),
        (0.75, -29, "9", "4 of 4", "12 of 16"),
        (0.75, -29, "9", "4 of 4", "12 of 16"),
        (0.75, -4, "25", "6 of 8", "12 of 16"),
        (0.75, -24, "30", "4 of 4", "12 of 16"),
        (0.75, -24, "30", "4 of 4", "12 of 16"),
    ]
    assert list(hits.drop(columns="note IDs").itertuples(index=False, name=None)) == [
        (number, *row) for number, row in enumerate(expected, 1)
    ]
    assert {number: list(hits.loc[number - 1, "note IDs"]) for number in NOTE_IDS} == NOTE_IDS


def test_printed_pitch_reuses_parse_and_hides_ids(H, reference, monkeypatch):
    import camat

    def do_not_parse(*args, **kwargs):
        pytest.fail("The second search parsed the same score again.")

    shown = []
    monkeypatch.setattr(camat, "parse_files", do_not_parse)
    monkeypatch.setitem(H, "display", shown.append)
    context, _ = reference
    hits = H["search"](context, every_pitch=False)
    assert hits["hit"].to_list() == [1, 2, 3, 4, 5, 6]
    assert hits["bars"].to_list() == ["1–2", "3–4", "4–5", "22–23", "25–26", "24–25"]
    assert hits["score"].to_list() == [1.0] * 5 + [0.875]
    assert hits["semitones"].to_list() == [0] * 6
    assert hits["cells"].to_list() == ["16 of 16"] * 5 + ["14 of 16"]
    [table] = shown
    assert "note IDs" not in table.data and "d418889e30" not in table.data


def test_chroma_smoke(H, reference):
    context, _ = reference
    hits = H["search"](context, chroma=True)
    assert set(hits.loc[hits["score"] == 1, "bars"]) >= {"1–2", "3–4", "4–5", "6–7", "22–23", "25–26"}


def test_write_and_move_finding(H, reference, edition, capsys):
    _, hits = reference
    path = edition["work"]
    before = path.read_bytes()
    assert H["draft_finding"](hits, 10) == DRAFT_10
    for label in LABELS:
        report = H["write_finding"](edition, hits, 10, label, SENTENCE)
        after = path.read_bytes()
        _expect_only_added_finding(before, after, 2)
        tree = ET.fromstring(after)
        [annot] = _finding(tree)
        assert _measures(tree)["2"][-1] is annot
        assert annot.get("type") == "finding"
        assert annot.get("label") == label
        assert annot.get("plist") == " ".join(f"#{i}" for i in NOTE_IDS[10])
        assert [p.text for p in annot.findall(f"{MEI}p")] == [DRAFT_10, SENTENCE]
        assert _notes(tree) == _notes(ET.fromstring(before))
        ids = [el.get(XML_ID) for el in tree.iter() if XML_ID in el.attrib]
        assert len(ids) == len(set(ids))
        assert report["works"][0]["notes"] == 1
        assert report["works"][0]["measures"] == 39
        assert Path(report["out"]).name == "_site"
        out = capsys.readouterr().out
        assert f"✓ work.mei: 1 finding, {label.replace('-', ' ')}, bars 2–3 (6 notes)" in out
        assert "✓ test build: 39 bars, 1 entry under Editorial notes; GitHub builds the same" in out

    _write_each_label(H, edition, hits, 1)
    moved = path.read_bytes()
    _expect_only_added_finding(before, moved, 1)
    tree = ET.fromstring(moved)
    [annot] = _finding(tree)
    assert _measures(tree)["1"][-1] is annot
    assert _notes(tree) == _notes(ET.fromstring(before))


def test_stale_hits_are_refused_and_a_finding_can_be_saved_again(H, reference, edition, capsys):
    _, hits = reference
    path = edition["work"]
    before = path.read_bytes()
    changed = before.replace(b'xml:id="d418889e265" pname="d"', b'xml:id="d418889e265" pname="c"', 1)
    assert changed != before
    path.write_bytes(changed)
    capsys.readouterr()
    warning = "! work.mei has changed since the search. Run the search cells again."

    assert _write_each_label(H, edition, hits, 10) == [None] * len(LABELS)
    assert path.read_bytes() == changed
    assert capsys.readouterr().out.splitlines() == [warning] * len(LABELS)
    H["show_hits"](edition, hits, [10, 11])
    assert capsys.readouterr().out.splitlines() == [warning]

    path.write_bytes(before)
    for label in LABELS:
        first = H["write_finding"](edition, hits, 10, label, SENTENCE)
        with_finding = path.read_bytes()
        second = H["write_finding"](edition, hits, 10, label, SENTENCE)
        assert first["works"][0]["notes"] == second["works"][0]["notes"] == 1
        assert path.read_bytes() == with_finding
    assert warning not in capsys.readouterr().out


def test_finding_needs_an_id_for_every_match(H, reference, edition, monkeypatch, capsys):
    path = edition["work"]
    before = path.read_bytes()
    missing_id = before.replace(b' xml:id="d418889e444"', b"", 1)
    assert missing_id != before
    path.write_bytes(missing_id)
    hits = H["search"](edition)
    [hit] = hits[hits["hit"] == 10].to_dict("records")
    assert hit["bars"] == "2–3" and hit["matched notes"] == "6 of 8"
    assert len(hit["note IDs"]) == 5
    capsys.readouterr()

    assert _write_each_label(H, edition, hits, 10) == [None] * len(LABELS)
    assert path.read_bytes() == missing_id
    assert capsys.readouterr().out.splitlines() == [
        "✗ Some matched notes have no xml:id in work.mei, so the finding could not link them. "
        "Ask your instructor to check work.mei. No change to work.mei."
    ] * len(LABELS)

    monkeypatch.setitem(H, "display", lambda output: None)
    monkeypatch.setitem(H, "_show_picture", lambda picture: None)
    H["show_hits"](edition, hits, [10])
    out = capsys.readouterr().out.splitlines()
    assert [line for line in out if line.startswith("!")] == [
        "! Some matched notes have no xml:id in work.mei, so they will not be highlighted."
    ]

    path.write_bytes(before)
    _write_each_label(H, edition, reference[1], 10)
    [annot] = _finding(ET.parse(path).getroot())
    assert annot.get("plist").split() == [f"#{note_id}" for note_id in NOTE_IDS[10]]


def test_hit_text_uses_singular_bar_for_one_measure(H, reference, edition, monkeypatch, capsys):
    _, hits = reference
    draft = H["draft_finding"](hits, 11)
    assert "hit 11: bar 3," in draft
    assert H["draft_finding"](hits, 10) == DRAFT_10

    monkeypatch.setitem(H, "display", lambda output: None)
    monkeypatch.setitem(H, "_show_picture", lambda picture: None)
    H["show_hits"](edition, hits, [11, 10])
    headings = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Hit ")]
    assert headings == [
        "Hit 11 · score 0.75 · 7 semitones lower than bar 1 · bar 3",
        "Hit 10 · score 0.75 · 5 semitones higher than bar 1 · bars 2–3",
    ]

    for label in LABELS:
        H["write_finding"](edition, hits, 11, label, SENTENCE)
        assert (f"✓ work.mei: 1 finding, {label.replace('-', ' ')}, bar 3 (4 notes)"
                in capsys.readouterr().out.splitlines())
    [annot] = _finding(ET.parse(edition["work"]).getroot())
    assert annot.find(f"{MEI}p").text == draft


@pytest.mark.parametrize(("other_entry", "notes_list"), [(False, "1 entry"), (True, "2 entries")])
def test_build_reports_entries_under_notes(H, reference, edition, capsys, other_entry, notes_list):
    if other_entry:
        path = edition["work"]
        marker = b'<pedal xml:id="seminar-pedal-1"'
        data = path.read_bytes()
        assert marker in data
        path.write_bytes(data.replace(
            marker, b'<annot xml:id="another-editorial-note"><p>Another observation.</p></annot>\n' + marker, 1
        ))
    _write_each_label(H, edition, reference[1], 10)
    assert (f"✓ test build: 39 bars, {notes_list} under Editorial notes; GitHub builds the same"
            in capsys.readouterr().out.splitlines())


@pytest.mark.parametrize(("number", "labels", "sentence", "message"), [
    (10, ("imitation",), SENTENCE, "Choose repeat, sequence-step or false-hit"),
    (10, LABELS, "", "Write your own sentence"),
    (10, LABELS, PLACEHOLDER, "Write your own sentence"),
    (0, LABELS, SENTENCE, "Choose a number from 1 to 23"),
    (24, LABELS, SENTENCE, "Choose a number from 1 to 23"),
])
def test_refusals_leave_bytes_alone(H, reference, edition, capsys, number, labels, sentence, message):
    _, hits = reference
    path = edition["work"]
    before = hashlib.sha256(path.read_bytes()).digest()
    for label in labels:
        H["write_finding"](edition, hits, number, label, sentence)
        assert hashlib.sha256(path.read_bytes()).digest() == before
        assert message in capsys.readouterr().out


def test_refuses_hand_reformatted_finding(H, reference, edition, capsys):
    _, hits = reference
    path = edition["work"]
    _write_each_label(H, edition, hits, 10)
    path.write_bytes(path.read_bytes().replace(b'type="finding" label=', b'type="finding"\n                label=', 1))
    before = hashlib.sha256(path.read_bytes()).digest()
    capsys.readouterr()
    for label in LABELS:
        H["write_finding"](edition, hits, 1, label, SENTENCE)
        assert hashlib.sha256(path.read_bytes()).digest() == before
        assert "Delete the old seminar-finding by hand" in capsys.readouterr().out


def test_sentence_is_escaped(H, reference, edition):
    _, hits = reference
    sentence = 'We see A & B, with rhythm < the length of the "held" note.'
    _write_each_label(H, edition, hits, 10, sentence)
    [annot] = _finding(ET.parse(edition["work"]).getroot())
    assert annot.findall(f"{MEI}p")[1].text == sentence


def test_site_config_is_required(H, reference, edition, capsys):
    _, hits = reference
    (edition["edition"] / "site.json").unlink()
    before = edition["work"].read_bytes()
    assert _write_each_label(H, edition, hits, 10) == [None] * len(LABELS)
    assert capsys.readouterr().out.count("Run 03_grieg_live_page.ipynb first") == len(LABELS)
    assert edition["work"].read_bytes() == before


def _rendered_notes(svg):
    return {el.attrib["id"]: el for el in ET.fromstring(svg).iter()
            if "note" in el.get("class", "").split()}


def test_query_highlights_call_and_landing(H, reference, monkeypatch, capsys):
    import matplotlib.pyplot as plt

    context, _ = reference
    output, scans, grids = [], [], []
    monkeypatch.setitem(H, "display", output.append)
    monkeypatch.setitem(H, "_show_picture", scans.append)
    monkeypatch.setattr(plt, "show", lambda: grids.append(plt.gca().images[0].get_array().copy()))
    H["show_query"](context)
    [svg] = output
    marked = {i for i, g in _rendered_notes(svg.data).items() if g.get("fill") == "#b32057"}
    assert marked == set(NOTE_IDS[1])
    assert len(scans) == 1
    [grid] = grids
    assert grid.shape == (9, 8) and grid.sum() == 16
    assert "10 notes, 16 filled cells, from bar 1 to the landing note in bar 2." in capsys.readouterr().out


def test_hit_score_and_scan_crops(H, reference, monkeypatch, capsys):
    context, hits = reference
    output, scans = [], []
    monkeypatch.setitem(H, "display", output.append)
    monkeypatch.setitem(H, "_show_picture", scans.append)

    H["show_hits"](context, hits, [4])
    [svg] = output
    notes = _rendered_notes(svg.data)
    marked = {i for i, g in notes.items() if g.get("fill") == "#b32057"}
    assert marked == set(hits.loc[3, "note IDs"]) & notes.keys()
    assert len(marked) == 10
    assert len(scans) == 1
    assert "7 semitones higher than bar 1" in capsys.readouterr().out

    scans.clear()
    H["show_hits"](context, hits, [3])
    assert len(scans) == 2

    scans.clear()
    H["show_hits"](context, hits, [10, 24])
    assert len(scans) == 1
    out = capsys.readouterr().out
    assert "12 of the 16 cells of the call are filled here; 6 of the 8 notes in this stretch match." in out
    assert "Choose a number from 1 to 23" in out


@pytest.fixture(scope="module")
def published(H, reference, tmp_path_factory):
    project = _copy_edition(tmp_path_factory.mktemp("published"))
    context = H["open_search_folder"](project.parent)
    _write_each_label(H, context, reference[1], 10)
    context["github"] = {"owner": "Owner", "repo": "repo"}
    return context


@pytest.mark.parametrize(("response", "message"), [
    ("same", "✓ Your finding is online. Click it under Editorial notes at https://owner.github.io/repo/#voglein/2"),
    ("older", "! The live page still has an older copy or no finding"),
    ("missing", "! The live page still has an older copy or no finding"),
    ("404", "! The score is not online yet"),
    ("offline", "✗ The live page could not be reached"),
])
def test_check_live_finding(H, published, monkeypatch, capsys, response, message):
    def urlopen(request, *, timeout):
        assert request.full_url == "https://owner.github.io/repo/mei/work.mei"
        assert dict(request.header_items())["User-agent"] == "camat-seminar"
        assert timeout == 30
        if response == "404":
            raise urllib.error.HTTPError(request.full_url, 404, "Not found", {}, None)
        if response == "offline":
            raise urllib.error.URLError("offline")
        data = published["work"].read_bytes()
        if response == "missing":
            data = (REFERENCE / "mei/work.mei").read_bytes()
        if response == "older":
            data = data.replace(b'plist="#d418889e265 ', b'plist="#d418889e285 ', 1)
        reply = io.BytesIO(data)
        reply.status = 200
        return reply

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    H["check_live_finding"](published)
    out = capsys.readouterr().out
    assert message in out
    if response in ("older", "missing"):
        assert "Wait a minute" in out and "Ctrl+Shift+R" in out and "Actions" in out


@pytest.mark.parametrize("response", ["short-read", "reset", "404"])
def test_live_finding_handles_a_dropped_download(H, published, monkeypatch, capsys, response):
    class DroppedReply(io.BytesIO):
        status = 200

        def read(self):
            if response == "short-read":
                raise IncompleteRead(b"<mei", 100)
            raise ConnectionResetError("connection reset")

    def urlopen(request, *, timeout):
        if response == "404":
            raise urllib.error.HTTPError(request.full_url, 404, "Not found", {}, None)
        return DroppedReply()

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    H["check_live_finding"](published)
    expected = ("! The score is not online yet at https://owner.github.io/repo/. Look at Actions on GitHub and try again."
                if response == "404"
                else "✗ The live page could not be reached. Check your internet connection and run this cell again.")
    assert capsys.readouterr().out.splitlines() == [expected]


def test_check_live_finding_needs_repository(H, edition, capsys):
    H["check_live_finding"](edition)
    assert "Run the repository check first" in capsys.readouterr().out


def test_open_search_folder_without_work(H, tmp_path, capsys):
    project = _copy_edition(tmp_path)
    (project / "edition/mei/work.mei").unlink()
    assert H["open_search_folder"](tmp_path) is None
    assert "Run 03_grieg_linking.ipynb" in capsys.readouterr().out
    assert not (project / "class_edition").exists()


def test_open_search_folder_with_changed_notes(H, tmp_path, capsys):
    project = _copy_edition(tmp_path)
    path = project / "edition/mei/work.mei"
    before = path.read_bytes()
    changed = before.replace(b'xml:id="d418889e30" pname="a"', b'xml:id="d418889e30" pname="g"', 1)
    assert changed != before
    path.write_bytes(changed)
    context = H["open_search_folder"](tmp_path)
    out = capsys.readouterr().out
    assert "Hit numbers may differ from the instructor's sheet, so check each hit by its bars." in out
    assert not H["search"](context).empty
    assert path.read_bytes() == changed


def test_check_repository_lists_unstaged_file_names_whole(H, tmp_path, monkeypatch, capsys):
    edition = tmp_path / "edition"
    (edition / "mei").mkdir(parents=True)
    work = edition / "mei/work.mei"
    work.write_text("<mei/>\n", encoding="utf-8")
    git = ["git", "-c", "user.name=T", "-c", "user.email=t@example.org"]
    for args in (["init", "-q", "-b", "main"], ["remote", "add", "origin", "https://github.com/someone/repo"],
                 ["add", "."], ["commit", "-q", "-m", "one"]):
        subprocess.run(git + args, cwd=edition, check=True)
    work.write_text("<mei><music/></mei>\n", encoding="utf-8")
    (edition / "notes.txt").write_text("new\n", encoding="utf-8")
    real = H["_git"]

    def no_network(context, *args):
        if args[0] == "ls-remote":
            return True, real(context, "rev-parse", "HEAD")[1] + "\trefs/heads/main"
        return real(context, *args)

    monkeypatch.setitem(H, "_git", no_network)
    H["check_repository"]({"edition": edition})
    assert "! Not committed yet (2): mei/work.mei, notes.txt" in capsys.readouterr().out
