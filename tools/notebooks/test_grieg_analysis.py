"""Offline tests for session 4 block 1: the class edition helper."""

from __future__ import annotations

import copy
import http.client
import io
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from collections import Counter

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[2]
HELPERS = Path(__file__).resolve().parent / "helpers"
WORK = ROOT / "sessions/03-linking-and-editing/notebooks/grieg_edition_work"
FIXTURE = ROOT / "sessions/04-publishing-and-analysis/fixtures/grieg-voglein-test-83eed567f"
REF_MEI = FIXTURE / "mei/work.mei"
REF_SHEET = FIXTURE / "reviews/page-42-system-1.md"
REF_COMMIT = "83eed567f"
# The session-3 files open_class_folder needs, plus the page images for graphic resolution.
PROJECT_FILES = ("inputs/settings.json", "inputs/sources.json",
                 "inputs/Grieg_Little_bird_Op43_No4.mei",
                 "edition/checkpoints/before-editing.mei",
                 "edition/pages/pages.json",
                 "edition/pages/page-0001.png",
                 "edition/pages/page-0002.png")
# Both inputs stay local: the reference fixture and an in-place run of the session 3 notebooks.
# Tests that read them skip without them; the others also run on a fresh clone.
LOCAL_INPUTS = [REF_MEI, REF_SHEET] + [WORK / rel for rel in PROJECT_FILES]


def _need_local_inputs():
    missing = [path for path in LOCAL_INPUTS if not path.is_file()]
    if missing:
        pytest.skip(f"needs {len(missing)} local input file(s), such as {missing[0].relative_to(ROOT)}")

MEI_NS = "http://www.music-encoding.org/ns/mei"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
MARKS = {"dynam", "tempo", "hairpin", "slur", "pedal", "dir", "fing", "octave"}


def _load_ns():
    """Load helpers the way the notebook does: join and exec into one namespace."""
    chunks = [(HELPERS / name).read_text(encoding="utf-8")
              for name in ("grieg_linking.py", "grieg_editing.py", "grieg_analysis.py")]
    ns = {"__name__": "grieg_analysis_test"}
    exec(compile("\n\n".join(chunks), str(HELPERS / "grieg_analysis.py"), "exec"), ns)
    return ns


@pytest.fixture(scope="module")
def H():
    return _load_ns()


def _name(el):
    return el.tag.split("}")[-1]


def _music_measures(root):
    music = root.find(f"{{{MEI_NS}}}music")
    return {m.get("n"): m for m in music.iter(f"{{{MEI_NS}}}measure")}


def _marks(measure):
    return [e for e in list(measure)
            if _name(e) in MARKS]


def _content_key_independent(element):
    """Expected content key by a path different from the helper's recursive tuple."""
    import xml.etree.ElementTree as ET
    clone = copy.deepcopy(element)

    def strip(el):
        if XML_ID in el.attrib:
            del el.attrib[XML_ID]
        el.text = " ".join((el.text or "").split()) or None
        el.tail = None
        for child in el:
            strip(child)
        # rebuild attrib sorted
        items = sorted(el.attrib.items())
        el.attrib.clear()
        for k, v in items:
            el.set(k, v)

    strip(clone)
    return ET.tostring(clone, encoding="unicode")


@pytest.fixture
def project(tmp_path):
    """A session-3 folder copy under pytest's temp dir (site/ via --basetemp)."""
    dest = tmp_path / "grieg_edition_work"
    _seed_minimal_project(dest)
    return dest


def _cache_write(project, owner, repo, commit, relative, data: bytes):
    folder = project / "class_edition/fetched" / f"{owner}__{repo}__{commit}"
    path = folder / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _parse(path):
    import xml.etree.ElementTree as ET
    return ET.parse(path).getroot()


def _write_mei(root, path):
    import xml.etree.ElementTree as ET
    ET.register_namespace("", MEI_NS)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _find_mark(measure, name, **attrs):
    for el in _marks(measure):
        if _name(el) != name:
            continue
        if all(el.get(k) == v for k, v in attrs.items()):
            return el
    return None


def _add_mark(measure, tag, xml_id=None, text=None, **attrs):
    import xml.etree.ElementTree as ET
    el = ET.SubElement(measure, f"{{{MEI_NS}}}{tag}")
    if xml_id:
        el.set(XML_ID, xml_id)
    for k, v in attrs.items():
        el.set(k, v)
    if text is not None:
        el.text = text
    return el


# --- Fixtures A–G -----------------------------------------------------------------

def _fixture_A():
    return REF_MEI.read_bytes(), REF_SHEET.read_bytes()


def _fixture_B():
    """bar-2 pp→p, no pedal, one extra hairpin."""
    root = _parse(REF_MEI)
    m2 = _music_measures(root)["2"]
    dynam = _find_mark(m2, "dynam", tstamp="1")
    assert dynam is not None and (dynam.text or "").strip() == "pp"
    dynam.text = "p"
    pedal = _find_mark(m2, "pedal")
    assert pedal is not None
    m2.remove(pedal)
    _add_mark(m2, "hairpin", xml_id="seminar-hairpin-b", form="cres", staff="1",
              place="below", tstamp="2", **{"tstamp2": "0m+6"})
    return _mei_bytes(root), None


def _mei_bytes(root):
    import xml.etree.ElementTree as ET
    ET.register_namespace("", MEI_NS)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _fixture_C():
    """42/3: hairpin+slur; duplicate pp; colliding dynam id; broken endid."""
    # Start from source-like before-editing content for notes; use reference as base copy
    root = _parse(WORK / "edition/checkpoints/before-editing.mei")
    # strip facsimile differences do not matter; add marks in bars 10-14
    measures = _music_measures(root)
    m10 = measures["10"]
    m11 = measures["11"]
    # duplicate the source pp in bar 10
    _add_mark(m10, "dynam", xml_id="seminar-dynam-dup", staff="1", place="below",
              tstamp="1", text="pp")
    # new dynam with colliding id
    _add_mark(m10, "dynam", xml_id="seminar-dynam-1", staff="1", place="above",
              tstamp="3", text="f")
    # hairpin and slur (valid endid from a note in bar 11)
    notes = [n for n in m11.iter(f"{{{MEI_NS}}}note") if n.get(XML_ID)]
    assert len(notes) >= 2
    _add_mark(m11, "hairpin", xml_id="seminar-hairpin-c", form="dim", staff="1",
              place="below", tstamp="1", **{"tstamp2": "0m+4"})
    _add_mark(m11, "slur", xml_id="seminar-slur-c", staff="1", curvedir="above",
              startid=f"#{notes[0].get(XML_ID)}", endid=f"#{notes[1].get(XML_ID)}")
    # broken mark
    _add_mark(m11, "slur", xml_id="seminar-slur-broken", staff="1", curvedir="below",
              startid=f"#{notes[0].get(XML_ID)}", endid="#no-such-element")
    return _mei_bytes(root), None


def _fixture_D():
    """43/2: change pname in bar 25 + new slur."""
    root = _parse(WORK / "edition/checkpoints/before-editing.mei")
    measures = _music_measures(root)
    m25 = measures["25"]
    note = next(n for n in m25.iter(f"{{{MEI_NS}}}note") if n.get("pname"))
    note.set("pname", "b" if note.get("pname") != "b" else "c")
    notes = [n for n in m25.iter(f"{{{MEI_NS}}}note") if n.get(XML_ID)]
    _add_mark(m25, "slur", xml_id="seminar-slur-d", staff="1", curvedir="above",
              startid=f"#{notes[0].get(XML_ID)}", endid=f"#{notes[-1].get(XML_ID)}")
    return _mei_bytes(root), None


def _fixture_E():
    """42/5: change bar-20 octave tstamp2."""
    root = _parse(WORK / "edition/checkpoints/before-editing.mei")
    m20 = _music_measures(root)["20"]
    octave = next(e for e in m20 if _name(e) == "octave")
    octave.set("tstamp2", "1m+1")
    return _mei_bytes(root), None


def _fixture_near_miss_whitespace():
    """Rewrite the source's own marks with different whitespace/attribute order: no changes."""
    import xml.etree.ElementTree as ET
    root = _parse(WORK / "inputs/Grieg_Little_bird_Op43_No4.mei")
    for measure in _music_measures(root).values():
        for el in list(_marks(measure)):
            tag = _name(el)
            attrs = dict(el.attrib)
            text = el.text
            measure.remove(el)
            neu = ET.Element(f"{{{MEI_NS}}}{tag}")
            for k in reversed(list(attrs)):
                neu.set(k, attrs[k])
            if text is not None:
                neu.text = f"  {text}  \n"
            measure.append(neu)
    return _mei_bytes(root), None


@pytest.fixture
def class_run(project, H, monkeypatch):
    """Seed cache for A–G, monkeypatch urlopen for F, build the class edition."""
    project  # ensure folder exists
    # Pre-create class_edition via open
    ctx = H["open_class_folder"](project.parent)  # cwd-style: parent contains grieg_edition_work
    # Actually open looks for grieg_edition_work in start; pass project.parent
    assert ctx["project"] == project.resolve()

    seeds = {
        ("egorpol", "grieg-voglein-test", REF_COMMIT): _fixture_A(),
        ("pair-b", "voglein-b", "bbbbbbb"): _fixture_B(),
        ("pair-c", "voglein-c", "ccccccc"): _fixture_C(),
        ("pair-d", "voglein-d", "ddddddd"): _fixture_D(),
        ("pair-e", "voglein-e", "eeeeeee"): _fixture_E(),
        ("pair-g1", "voglein-g1", "1111111"): _fixture_A(),
        ("pair-g2", "voglein-g2", "2222222"): _fixture_A(),
        ("pair-ws", "voglein-ws", "abcdef0"): _fixture_near_miss_whitespace(),
    }
    for (owner, repo, commit), (mei, sheet) in seeds.items():
        _cache_write(project, owner, repo, commit, "mei/work.mei", mei)
        page_sys = {
            REF_COMMIT: (42, 1),
            "bbbbbbb": (42, 1),
            "ccccccc": (42, 3),
            "ddddddd": (43, 2),
            "eeeeeee": (42, 5),
            "1111111": (43, 1),
            "2222222": (43, 1),
            "abcdef0": (42, 1),
        }[commit]
        if sheet is not None:
            rel = f"reviews/page-{page_sys[0]}-system-{page_sys[1]}.md"
            _cache_write(project, owner, repo, commit, rel, sheet)

    class_list = """\
page,system,pair,repository,commit,use
42,1,Reference,egorpol/grieg-voglein-test,83eed567f,yes
42,1,PairB,pair-b/voglein-b,bbbbbbb,
42,3,PairC,pair-c/voglein-c,ccccccc,yes
43,2,PairD,pair-d/voglein-d,ddddddd,yes
42,5,PairE,pair-e/voglein-e,eeeeeee,yes
43,4,PairF,pair-f/voglein-f,fffffff,yes
43,1,PairG1,pair-g1/voglein-g1,1111111,
43,1,PairG2,pair-g2/voglein-g2,2222222,
"""

    real_urlopen = urllib.request.urlopen

    def fake_urlopen(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else str(request)
        if str(url).startswith("file:"):
            return real_urlopen(request, timeout=timeout)
        if "fffffff" in str(url):
            raise urllib.error.HTTPError(str(url), 404, "Not Found", hdrs=None, fp=None)
        # Missing review sheets etc.: 404, never cache a failure
        raise urllib.error.HTTPError(str(url), 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    rows, picked = H["read_class_list"](class_list, ctx)
    H["fetch_class"](ctx, rows)
    coverage = H["build_class_edition"](ctx, rows, picked)
    return ctx, rows, picked, coverage


# --- Tests ------------------------------------------------------------------------

def test_open_class_folder(project, H):
    ctx = H["open_class_folder"](project.parent)
    assert ctx["project"] == project.resolve()
    assert ctx["class_edition"] == project.resolve() / "class_edition"
    assert len(ctx["layout_systems"]) == 10
    assert ctx["layout_systems"][0][:2] == ("42", 1)
    assert ctx["layout_systems"][0][2] == ["1", "2", "3", "4"]


def test_open_class_folder_missing(tmp_path, H):
    with pytest.raises(FileNotFoundError, match="03_grieg_linking"):
        H["open_class_folder"](tmp_path)


def _seed_minimal_project(dest):
    """Copy the files open_class_folder requires into dest."""
    _need_local_inputs()
    for rel in PROJECT_FILES:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORK / rel, target)


def test_open_class_folder_candidate_3(tmp_path, H):
    """Instructor layout: start in sessions/04/…/notebooks → ../../03/…/notebooks/grieg_edition_work."""
    project = (tmp_path / "sessions/03-linking-and-editing/notebooks/grieg_edition_work")
    _seed_minimal_project(project)
    start = tmp_path / "sessions/04-publishing-and-analysis/notebooks"
    start.mkdir(parents=True)
    ctx = H["open_class_folder"](start)
    assert ctx["project"] == project.resolve()
    assert (ctx["class_edition"] / "fetched").is_dir()
    assert ctx["class_edition"].is_relative_to(tmp_path)


def test_open_class_folder_candidate_4(tmp_path, H):
    """Instructor layout: start at repo root → sessions/03/…/notebooks/grieg_edition_work."""
    project = tmp_path / "sessions/03-linking-and-editing/notebooks/grieg_edition_work"
    _seed_minimal_project(project)
    ctx = H["open_class_folder"](tmp_path)
    assert ctx["project"] == project.resolve()
    assert ctx["class_edition"].is_relative_to(tmp_path)


def test_open_class_folder_too_deep(tmp_path, H):
    """One folder deeper than candidate 3 expects: no walk up, session-3 message."""
    project = tmp_path / "sessions/03-linking-and-editing/notebooks/grieg_edition_work"
    _seed_minimal_project(project)
    start = tmp_path / "sessions/04-publishing-and-analysis/notebooks/sub"
    start.mkdir(parents=True)
    with pytest.raises(FileNotFoundError, match="03_grieg_linking"):
        H["open_class_folder"](start)
    assert not (project / "class_edition").exists()


def test_class_list_parsing(project, H):
    ctx = H["open_class_folder"](project.parent)
    text = """
page,system,pair,repository,commit,use
42,1,A,https://github.com/Own/Repo.git,abcdef1,yes
42,2,B,Own2/Repo2/,1234567,
42,3,C,https://github.com/o/r/,abcdef0,

42,9,Bad,o/r,abcdef1,yes
42,1,BadCommit,o/r,xyz,yes
43,1,WS ,  egorpol/grieg-voglein-test  ,  83eed567f  , yes
"""
    rows, picked = H["read_class_list"](text, ctx)
    repos = {r["pair"]: r["repository"] for r in rows}
    assert repos["A"] == "Own/Repo"
    assert repos["B"] == "Own2/Repo2"
    assert repos["C"] == "o/r"
    assert "Bad" not in repos
    assert "BadCommit" not in repos
    assert picked[_system_key_h(H, 42, 1)]["pair"] == "A"
    # missing header
    rows2, _ = H["read_class_list"]("42,1,A,o/r,abcdef1,yes\n", ctx)
    assert rows2 == []


def _system_key_h(H, page, system):
    return H["_system_key"](page, system)


def test_fetch_urlopen_and_cache(project, H, monkeypatch):
    ctx = H["open_class_folder"](project.parent)
    seen = {}

    class Resp:
        def __init__(self, data):
            self._data = data
        def read(self):
            return self._data
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_urlopen(request, timeout=None):
        url = request.full_url
        ua = request.headers.get("User-agent") or request.headers.get("User-Agent")
        seen["url"] = url
        seen["ua"] = ua
        seen["timeout"] = timeout
        if "badcommit" in url:
            raise urllib.error.HTTPError(url, 404, "Not Found", hdrs=None, fp=None)
        if "noconnect" in url:
            raise urllib.error.URLError("down")
        if url.endswith("mei/work.mei"):
            return Resp(REF_MEI.read_bytes())
        if "reviews/" in url:
            return Resp(REF_SHEET.read_bytes())
        raise urllib.error.HTTPError(url, 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    row = {
        "owner": "egorpol", "repo": "grieg-voglein-test", "commit": REF_COMMIT,
        "page": "42", "system": 1, "pair": "Ref", "repository": "egorpol/grieg-voglein-test",
        "bars": ["1", "2", "3", "4"], "use": True,
    }
    path, status = H["fetch_pair"](ctx, row, relative="mei/work.mei")
    assert status == "fetched"
    assert path.is_file()
    assert seen["url"] == f"https://raw.githubusercontent.com/egorpol/grieg-voglein-test/{REF_COMMIT}/mei/work.mei"
    assert seen["ua"] == "camat-seminar"
    assert seen["timeout"] == 30

    # second run hits cache even if urlopen raises
    def boom(request, timeout=None):
        raise RuntimeError("network should not be used")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    path2, status2 = H["fetch_pair"](ctx, row, relative="mei/work.mei")
    assert status2 == "cached"
    assert path2 == path

    # 404 not cached
    bad = dict(row, commit="badcommit")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    path3, status3 = H["fetch_pair"](ctx, bad, relative="mei/work.mei")
    assert status3 == "404" and path3 is None
    assert not (ctx["class_edition"] / "fetched/egorpol__grieg-voglein-test__badcommit/mei/work.mei").exists()

    down = dict(row, owner="x", repo="noconnect", commit="abcdef0")
    path4, status4 = H["fetch_pair"](ctx, down, relative="mei/work.mei")
    assert status4 == "no connection" and path4 is None


@pytest.mark.parametrize("error", [
    http.client.IncompleteRead(b"abc", 97),
    ConnectionResetError(104, "Connection reset by peer"),
])
def test_fetch_dropped_download_is_no_connection(project, H, monkeypatch, error):
    ctx = H["open_class_folder"](project.parent)

    class Broken:
        def read(self):
            raise error
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda request, timeout=None: Broken())
    row = {"owner": "x", "repo": "dropped", "commit": "abcdef1"}
    path, status = H["fetch_pair"](ctx, row, relative="mei/work.mei")
    assert status == "no connection" and path is None
    assert not (ctx["class_edition"] / "fetched/x__dropped__abcdef1/mei/work.mei").exists()


def test_fixture_merge_and_coverage(class_run, H):
    ctx, rows, picked, coverage = class_run
    assert coverage is not None
    assert len(coverage) == 10

    by = {(str(r.page), int(r.system)): r for r in coverage.itertuples()}
    assert by[("42", 1)].status == "merged"
    assert by[("42", 3)].status == "merged"
    assert by[("42", 5)].status == "merged"
    assert by[("43", 2)].status == "notes differ"
    assert by[("43", 4)].status == "not fetched"
    assert by[("43", 1)].status == "several versions, none picked"
    for key in (("42", 2), ("42", 4), ("43", 3), ("43", 5)):
        assert by[key].status == "gap: no pair"

    # Case A expectations via independent ElementTree count
    root = _parse(ctx["class_mei"])
    measures = _music_measures(root)
    m2 = measures["2"]
    kinds = Counter(_name(e) for e in _marks(m2))
    assert kinds["dynam"] == 1 and kinds["slur"] == 1 and kinds["pedal"] == 1
    dynam = _find_mark(m2, "dynam")
    assert (dynam.text or "").strip() == "pp"
    # bar-15 f outside → not in class edition
    assert _find_mark(measures["15"], "dynam") is None

    # Review sheet summary for A
    assert "3 of 4 decided" in by[("42", 1)].review_sheet
    assert "1 accept" in by[("42", 1)].review_sheet
    assert "1 correct" in by[("42", 1)].review_sheet
    assert "1 unresolved" in by[("42", 1)].review_sheet
    assert "1 not readable" in by[("42", 1)].review_sheet

    # Case C: hairpin+slur merged; one pp in bar 10; renamed dynam; broken refused
    m10 = measures["10"]
    m11 = measures["11"]
    pps = [e for e in _marks(m10) if _name(e) == "dynam" and (e.text or "").strip() == "pp"]
    assert len(pps) == 1
    assert _find_mark(m11, "hairpin") is not None
    assert _find_mark(m11, "slur", **{XML_ID: "seminar-slur-c"}) is not None or any(
        _name(e) == "slur" and e.get(XML_ID) == "seminar-slur-c" for e in _marks(m11)
    )
    # colliding id renamed
    ids = [e.get(XML_ID) for e in _marks(m10) if _name(e) == "dynam" and (e.text or "").strip() == "f"]
    assert ids and ids[0] == "seminar-dynam-1-p42s3"
    assert not any(e.get(XML_ID) == "seminar-slur-broken" for e in measures["11"].iter())

    # Case E: one octave with new tstamp2
    octaves = [e for e in _marks(measures["20"]) if _name(e) == "octave"]
    assert len(octaves) == 1
    assert octaves[0].get("tstamp2") == "1m+1"

    # Case D: nothing from D
    assert not any(
        (e.get(XML_ID) or "").startswith("seminar-slur-d")
        for e in measures["25"].iter()
    )

    # Notes identical to source; no duplicate xml:id; graphics resolve; not under edition/
    source = _parse(ctx["mei"])
    ok, bad = H["notes_equal"](source, root)
    assert ok, bad
    seen = {}
    for e in root.iter():
        i = e.get(XML_ID)
        if i:
            assert i not in seen, i
            seen[i] = e
    for g in root.iter(f"{{{MEI_NS}}}graphic"):
        target = (ctx["class_mei"].parent / g.get("target")).resolve()
        assert target.is_file(), g.get("target")
    assert "edition" not in ctx["class_mei"].relative_to(ctx["project"]).parts[:1]
    assert ctx["class_mei"].parent == ctx["class_edition"]


def test_coverage_counts_only_applied_marks(class_run, H, capsys):
    """Case C's duplicate pp and broken slur are refused: neither counts as added."""
    ctx, rows, picked, coverage = class_run
    by = {(str(r.page), int(r.system)): r for r in coverage.itertuples()}
    row = by[("42", 3)]
    assert (row.status, row.marks_added, row.refused) == ("merged", "dynam 1, hairpin 1, slur 1", 2)
    # The same count by another path: marks in bars 10–14 of the class edition minus the base's
    base = _music_measures(_parse(ctx["before"]))
    merged = _music_measures(_parse(ctx["class_mei"]))
    added = Counter()
    for bar in ("10", "11", "12", "13", "14"):
        added += Counter(_name(e) for e in _marks(merged[bar])) - Counter(_name(e) for e in _marks(base[bar]))
    assert added == Counter({"dynam": 1, "hairpin": 1, "slur": 1})
    assert all(r.refused == 0 for key, r in by.items() if key != ("42", 3))
    capsys.readouterr()
    H["build_class_edition"](ctx, rows, picked)
    out = capsys.readouterr().out.splitlines()
    assert ("✓ Merged page 42, system 3 from pair-c/voglein-c@ccccccc "
            "(dynam 1, hairpin 1, slur 1; 2 refused).") in out


def test_nested_mark_is_refused_with_its_holder(project, H, monkeypatch, capsys):
    """A mark inside another mark: both are refused and counted, and neither reaches the file."""
    ctx = H["open_class_folder"](project.parent)
    root = _parse(WORK / "edition/checkpoints/before-editing.mei")
    m10 = _music_measures(root)["10"]
    holder = _add_mark(m10, "dir", xml_id="seminar-dir-nested", staff="1", place="above",
                       tstamp="1", text="dolce")
    _add_mark(holder, "slur", xml_id="seminar-slur-nested", staff="1", endid="#missing-note")
    _add_mark(m10, "hairpin", xml_id="seminar-hairpin-n", form="cres", staff="1", place="below",
              tstamp="1", **{"tstamp2": "0m+3"})
    _cache_write(project, "pair-n", "voglein-n", "9999999", "mei/work.mei", _mei_bytes(root))
    _offline_urlopen(monkeypatch)
    text = "page,system,pair,repository,commit,use\n42,3,PairN,pair-n/voglein-n,9999999,yes\n"
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)
    coverage = H["build_class_edition"](ctx, rows, picked)
    out = capsys.readouterr().out
    row = {(str(r.page), int(r.system)): r for r in coverage.itertuples()}[("42", 3)]
    assert (row.status, row.marks_added, row.refused) == ("merged", "hairpin 1", 2)
    ids = {e.get(XML_ID) for e in _parse(ctx["class_mei"]).iter()}
    assert "seminar-hairpin-n" in ids
    assert not ids & {"seminar-dir-nested", "seminar-slur-nested"}
    assert out.count("a mark inside another mark") == 2


def test_other_versions_B_vs_A(class_run, H, capsys):
    ctx, rows, picked, coverage = class_run
    H["compare_other_versions"](ctx)
    out = capsys.readouterr().out
    assert "PairB" in out or "pair-b" in out.lower() or "vs PairB" in out
    # three differences: pp→p, missing pedal, extra hairpin
    assert "only in the picked version" in out
    assert "only in PairB" in out
    assert "pedal" in out.lower() or "<pedal>" in out
    assert "hairpin" in out.lower() or "<hairpin>" in out
    assert "dynam" in out.lower() or "<dynam>" in out


def test_byte_identical_rerun(class_run, H):
    ctx, rows, picked, coverage = class_run
    mei1 = ctx["class_mei"].read_bytes()
    csv1 = ctx["coverage_csv"].read_bytes()
    coverage2 = H["build_class_edition"](ctx, rows, picked)
    assert coverage2 is not None
    assert ctx["class_mei"].read_bytes() == mei1
    assert ctx["coverage_csv"].read_bytes() == csv1


def _offline_urlopen(monkeypatch):
    real = urllib.request.urlopen

    def fake(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else str(request)
        if str(url).startswith("file:"):
            return real(request, timeout=timeout)
        raise urllib.error.HTTPError(str(url), 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setattr(urllib.request, "urlopen", fake)


def test_near_miss_whitespace_and_header(project, H, monkeypatch):
    ctx = H["open_class_folder"](project.parent)
    mei, _ = _fixture_near_miss_whitespace()
    _cache_write(project, "pair-ws", "voglein-ws", "abcdef0", "mei/work.mei", mei)
    _offline_urlopen(monkeypatch)
    text = "page,system,pair,repository,commit,use\n42,1,WS,pair-ws/voglein-ws,abcdef0,yes\n"
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)
    source = _parse(ctx["mei"])
    pair = _parse(rows[0]["mei_path"])
    changes = H["pair_changes"](source, pair, rows[0]["bars"])
    assert changes["added"] == []
    assert changes["removed"] == []
    assert changes["changed"] == []
    assert changes["outside"] == []
    # header/facsimile differ on reference but other changes inside measures should be 0
    _cache_write(project, "egorpol", "grieg-voglein-test", "aaaaaaa", "mei/work.mei",
                 REF_MEI.read_bytes())
    text2 = "page,system,pair,repository,commit,use\n42,1,R,egorpol/grieg-voglein-test,aaaaaaa,yes\n"
    rows2, _ = H["read_class_list"](text2, ctx)
    H["fetch_class"](ctx, rows2)
    changes2 = H["pair_changes"](source, _parse(rows2[0]["mei_path"]), rows2[0]["bars"])
    assert sum(n for _, n in changes2["other"]) == 0


def _camat_tables(path):
    from camat import parse_files

    results, _, _ = parse_files(
        [str(path)], backend="none", display_preview_df_pitch=False,
        display_preview_df_events=False, include_xml_ids=True,
        parse_enharmonic=True, quiet_native_warnings=True,
    )
    return results[0]["df_pitch"], results[0]["df_events"]


def test_statistics_smoke(class_run, H):
    ctx, rows, picked, coverage = class_run
    path = H["class_edition_for_camat"](ctx)
    df_pitch, df_events = _camat_tables(path)
    music = _parse(ctx["class_mei"]).find(f"{{{MEI_NS}}}music")
    tie_ends = {tie.get("endid").lstrip("#") for tie in music.iter(f"{{{MEI_NS}}}tie")}
    note_count = sum(note.get(XML_ID) not in tie_ends for note in music.iter(f"{{{MEI_NS}}}note"))
    assert len(df_pitch) == note_count == 479
    bar2 = df_events[df_events["Measure"] == 2]
    types = set(bar2["type"])
    assert "slur" in types and "pedal" in types and "dynamic" in types
    assert H["plot_marks_per_bar"](ctx, df_events) is not None


def test_duplicate_check_planted_failure(project, H, monkeypatch):
    """Show that removing the duplicate check would accept a second pp in bar 10."""
    ctx = H["open_class_folder"](project.parent)
    _cache_write(project, "egorpol", "grieg-voglein-test", REF_COMMIT, "mei/work.mei",
                 REF_MEI.read_bytes())
    _cache_write(project, "egorpol", "grieg-voglein-test", REF_COMMIT,
                 "reviews/page-42-system-1.md", REF_SHEET.read_bytes())
    mei_c, _ = _fixture_C()
    _cache_write(project, "pair-c", "voglein-c", "ccccccc", "mei/work.mei", mei_c)
    _offline_urlopen(monkeypatch)
    text = """\
page,system,pair,repository,commit,use
42,1,Reference,egorpol/grieg-voglein-test,83eed567f,yes
42,3,PairC,pair-c/voglein-c,ccccccc,yes
"""
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)

    # With the check: exactly one pp
    H["build_class_edition"](ctx, rows, picked)
    root = _parse(ctx["class_mei"])
    pps = [e for e in _marks(_music_measures(root)["10"])
           if _name(e) == "dynam" and (e.text or "").strip() == "pp"]
    assert len(pps) == 1

    # Planted failure: bypass duplicate check
    original = H["build_class_edition"]
    real_find = H["_find_mark_by_key"]

    def find_no_dup(measure, key):
        # pretend bar never has the mark when checking duplicates for dynam pp
        return None

    # Patch _find_mark_by_key only for the duplicate refusal path by wrapping build
    calls = {"dup_would_pass": False}
    real_build_parts = H["_find_mark_by_key"]

    def sneaky_find(measure, key):
        found = real_build_parts(measure, key)
        # When the duplicate pp key is sought and found, pretend missing so addition proceeds
        if found is not None and key[0] == "dynam" and key[2] == "pp":
            calls["dup_would_pass"] = True
            return None
        return found

    H["_find_mark_by_key"] = sneaky_find
    # rebuild from clean before-editing by deleting class mei and rebuilding
    if ctx["class_mei"].exists():
        ctx["class_mei"].unlink()
    H["build_class_edition"](ctx, rows, picked)
    H["_find_mark_by_key"] = real_build_parts
    root2 = _parse(ctx["class_mei"])
    pps2 = [e for e in _marks(_music_measures(root2)["10"])
            if _name(e) == "dynam" and (e.text or "").strip() == "pp"]
    assert calls["dup_would_pass"], "planted bypass did not trigger"
    assert len(pps2) == 2, "without the duplicate check, bar 10 would hold two pp marks"

    # Put the check back and confirm one pp again
    if ctx["class_mei"].exists():
        ctx["class_mei"].unlink()
    H["build_class_edition"](ctx, rows, picked)
    root3 = _parse(ctx["class_mei"])
    pps3 = [e for e in _marks(_music_measures(root3)["10"])
            if _name(e) == "dynam" and (e.text or "").strip() == "pp"]
    assert len(pps3) == 1


def test_notes_equal_swapped_measures(project, H):
    source = _parse(project / "inputs/Grieg_Little_bird_Op43_No4.mei")
    other = _parse(project / "inputs/Grieg_Little_bird_Op43_No4.mei")
    music = other.find(f"{{{MEI_NS}}}music")
    # Find the parent that holds consecutive measures 2 and 3 and swap them
    measures = [m for m in music.iter(f"{{{MEI_NS}}}measure") if m.get("n")]
    m2 = next(m for m in measures if m.get("n") == "2")
    m3 = next(m for m in measures if m.get("n") == "3")
    parent = None
    for candidate in music.iter():
        children = list(candidate)
        if m2 in children and m3 in children:
            parent = candidate
            break
    assert parent is not None
    children = list(parent)
    i2, i3 = children.index(m2), children.index(m3)
    children[i2], children[i3] = children[i3], children[i2]
    parent[:] = children
    # Independent check of the sequence
    seq = [m.get("n") for m in other.find(f"{{{MEI_NS}}}music").iter(f"{{{MEI_NS}}}measure") if m.get("n")]
    assert seq[seq.index("3") + 0] == "3" and "2" in seq
    assert seq.index("3") < seq.index("2")
    ok, bad = H["notes_equal"](source, other)
    assert ok is False
    assert "2" in bad and "3" in bad


def test_notes_equal_duplicate_measure_n(project, H):
    source = _parse(project / "inputs/Grieg_Little_bird_Op43_No4.mei")
    other = _parse(project / "inputs/Grieg_Little_bird_Op43_No4.mei")
    m5 = next(m for m in other.find(f"{{{MEI_NS}}}music").iter(f"{{{MEI_NS}}}measure")
              if m.get("n") == "5")
    m5.set("n", "4")
    ns = [m.get("n") for m in other.find(f"{{{MEI_NS}}}music").iter(f"{{{MEI_NS}}}measure") if m.get("n")]
    assert ns.count("4") == 2 and "5" not in ns
    ok, bad = H["notes_equal"](source, other)
    assert ok is False
    assert "4" in bad


def test_other_keys_dir_with_rend_not_other(project, H):
    source = _parse(project / "inputs/Grieg_Little_bird_Op43_No4.mei")
    pair = _parse(project / "edition/checkpoints/before-editing.mei")
    m2 = _music_measures(pair)["2"]
    import xml.etree.ElementTree as ET
    direction = ET.SubElement(m2, f"{{{MEI_NS}}}dir",
                              {XML_ID: "seminar-dir-1", "staff": "1", "tstamp": "1"})
    rend = ET.SubElement(direction, f"{{{MEI_NS}}}rend", {"fontstyle": "italic"})
    rend.text = "dolce"
    changes = H["pair_changes"](source, pair, ["1", "2", "3", "4"])
    assert len(changes["added"]) == 1
    assert _name(changes["added"][0][1]) == "dir"
    assert sum(n for _, n in changes["other"]) == 0


def test_other_keys_changed_artic_is_other(project, H):
    source = _parse(project / "inputs/Grieg_Little_bird_Op43_No4.mei")
    pair = _parse(project / "edition/checkpoints/before-editing.mei")
    # Change one artic inside a note in bar 2 (independent of marks)
    m2 = _music_measures(pair)["2"]
    artic = next(e for e in m2.iter(f"{{{MEI_NS}}}artic"))
    before = artic.get("artic") or (artic.text or "")
    artic.set("artic", "acc" if before != "acc" else "stacc")
    changes = H["pair_changes"](source, pair, ["1", "2", "3", "4"])
    assert changes["added"] == []
    assert sum(n for _, n in changes["other"]) >= 1
    assert any(bar == "2" for bar, _ in changes["other"])


def test_rename_collision_appends_number(project, H, monkeypatch, capsys):
    """Base already has seminar-dynam-1 and seminar-dynam-1-p42s3; C's id becomes …-p42s3-2."""
    ctx = H["open_class_folder"](project.parent)
    before = _parse(project / "edition/checkpoints/before-editing.mei")
    m1 = _music_measures(before)["1"]
    _add_mark(m1, "dynam", xml_id="seminar-dynam-1", staff="1", place="above",
              tstamp="6", text="mf")
    _add_mark(m1, "dynam", xml_id="seminar-dynam-1-p42s3", staff="2", place="below",
              tstamp="6", text="mp")
    _write_mei(before, project / "edition/checkpoints/before-editing.mei")
    mei_c, _ = _fixture_C()
    _cache_write(project, "pair-c", "voglein-c", "ccccccc", "mei/work.mei", mei_c)
    _offline_urlopen(monkeypatch)
    text = "page,system,pair,repository,commit,use\n42,3,PairC,pair-c/voglein-c,ccccccc,yes\n"
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)
    H["build_class_edition"](ctx, rows, picked)
    out = capsys.readouterr().out
    assert "seminar-dynam-1 → seminar-dynam-1-p42s3-2" in out
    root = _parse(ctx["class_mei"])
    ids = [e.get(XML_ID) for e in root.iter() if e.get(XML_ID)]
    assert "seminar-dynam-1-p42s3-2" in ids
    assert len(ids) == len(set(ids))
    # Independent: the renamed dynam *f* lives in bar 10
    f_marks = [e for e in _marks(_music_measures(root)["10"])
               if _name(e) == "dynam" and (e.text or "").strip() == "f"]
    assert len(f_marks) == 1 and f_marks[0].get(XML_ID) == "seminar-dynam-1-p42s3-2"


def test_pointers_without_hash(project, H, monkeypatch):
    ctx = H["open_class_folder"](project.parent)
    root = _parse(project / "edition/checkpoints/before-editing.mei")
    m2 = _music_measures(root)["2"]
    notes = [n for n in m2.iter(f"{{{MEI_NS}}}note") if n.get(XML_ID)]
    assert len(notes) >= 2
    good_id = notes[1].get(XML_ID)
    _add_mark(m2, "slur", xml_id="seminar-slur-hashless-good", staff="1", curvedir="above",
              startid=f"#{notes[0].get(XML_ID)}", endid=good_id)  # no '#'
    _add_mark(m2, "slur", xml_id="seminar-slur-hashless-bad", staff="1", curvedir="below",
              startid=f"#{notes[0].get(XML_ID)}", endid="nonexistent")
    data = _mei_bytes(root)
    _cache_write(project, "pair-p", "voglein-p", "aaaaaa1", "mei/work.mei", data)
    _offline_urlopen(monkeypatch)
    text = "page,system,pair,repository,commit,use\n42,1,Ptr,pair-p/voglein-p,aaaaaa1,yes\n"
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)
    H["build_class_edition"](ctx, rows, picked)
    edition = _parse(ctx["class_mei"])
    m2e = _music_measures(edition)["2"]
    ids = {e.get(XML_ID) for e in m2e.iter() if e.get(XML_ID)}
    assert "seminar-slur-hashless-good" in ids
    assert "seminar-slur-hashless-bad" not in ids
    good = next(e for e in _marks(m2e) if e.get(XML_ID) == "seminar-slur-hashless-good")
    assert good.get("endid") == good_id


def test_plot_marks_per_bar_shading(project, H, monkeypatch):
    """Only 42/1 merged: shading covers positions of bars 5–39, not 1–4; 39 x positions."""
    from matplotlib.patches import Rectangle
    ctx = H["open_class_folder"](project.parent)
    _cache_write(project, "egorpol", "grieg-voglein-test", REF_COMMIT, "mei/work.mei",
                 REF_MEI.read_bytes())
    _cache_write(project, "egorpol", "grieg-voglein-test", REF_COMMIT,
                 "reviews/page-42-system-1.md", REF_SHEET.read_bytes())
    _offline_urlopen(monkeypatch)
    text = ("page,system,pair,repository,commit,use\n"
            "42,1,Reference,egorpol/grieg-voglein-test,83eed567f,yes\n")
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)
    H["build_class_edition"](ctx, rows, picked)
    _, df_events = _camat_tables(H["class_edition_for_camat"](ctx))
    ax = H["plot_marks_per_bar"](ctx, df_events)
    assert ax is not None
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert labels == [str(i) for i in range(1, 40)]
    # Independent mark count in bar 2 from the written file
    root = _parse(ctx["class_mei"])
    bar2_kinds = Counter(_name(e) for e in _marks(_music_measures(root)["2"]))
    assert bar2_kinds["slur"] == 1 and bar2_kinds["pedal"] == 1 and bar2_kinds["dynam"] == 1
    # Stacked bar height at x position of bar 2 (index 1); bar patches have width 0.85
    bar2_height = sum(
        p.get_height() for p in ax.patches
        if isinstance(p, Rectangle) and abs(p.get_width() - 0.85) < 0.05
        and abs(p.get_x() + p.get_width() / 2 - 1) < 0.2
    )
    assert bar2_height == sum(bar2_kinds.values()) == 3
    # axvspan is a full-height Rectangle (width 1.0) under a blended transform
    shaded = [
        p.get_x() + p.get_width() / 2
        for p in ax.patches
        if isinstance(p, Rectangle) and abs(p.get_width() - 1.0) < 1e-6
    ]
    for pos in range(4):
        assert not any(abs(c - pos) < 0.1 for c in shaded), f"bar {pos + 1} should not be shaded"
    for pos in range(4, 39):
        assert any(abs(c - pos) < 0.1 for c in shaded), f"bar {pos + 1} should be shaded"
    # Bar 1: the music has one p; the header incipit's p must not be counted again
    bar1_dynam = sum(1 for e in _marks(_music_measures(root)["1"]) if _name(e) == "dynam")
    assert bar1_dynam == 1
    bar1_height = sum(
        p.get_height() for p in ax.patches
        if isinstance(p, Rectangle) and abs(p.get_width() - 0.85) < 0.05
        and abs(p.get_x() + p.get_width() / 2 - 0) < 0.2
    )
    assert bar1_height == bar1_dynam
    # Counts are whole numbers: no 0.5 steps on the y axis
    assert all(float(tick).is_integer() for tick in ax.get_yticks())


def test_class_edition_for_camat_leaves_out_incipit(project, H, monkeypatch, capsys):
    """CAMAT reads the class edition without its header incipit; the file itself keeps it."""
    ctx = H["open_class_folder"](project.parent)
    capsys.readouterr()
    assert H["class_edition_for_camat"](ctx) is None
    assert capsys.readouterr().out == "Skipped. Build the class edition first.\n"
    assert not (project / "class_edition/for_camat").exists()
    _cache_write(project, "egorpol", "grieg-voglein-test", REF_COMMIT, "mei/work.mei",
                 REF_MEI.read_bytes())
    _cache_write(project, "egorpol", "grieg-voglein-test", REF_COMMIT,
                 "reviews/page-42-system-1.md", REF_SHEET.read_bytes())
    _offline_urlopen(monkeypatch)
    text = ("page,system,pair,repository,commit,use\n"
            "42,1,Reference,egorpol/grieg-voglein-test,83eed567f,yes\n")
    rows, picked = H["read_class_list"](text, ctx)
    H["fetch_class"](ctx, rows)
    H["build_class_edition"](ctx, rows, picked)
    path = ctx["class_mei"]
    before = path.read_bytes()
    root = _parse(path)
    incipits = list(root.find(f"{{{MEI_NS}}}meiHead").iter(f"{{{MEI_NS}}}incip"))
    assert len(incipits) == 1
    head_dynam = sum(1 for _ in incipits[0].iter(f"{{{MEI_NS}}}dynam"))
    assert head_dynam >= 1  # otherwise this test proves nothing
    copy_path = H["class_edition_for_camat"](ctx)
    assert copy_path == project / "class_edition/for_camat/class-edition.mei"
    assert not list(_parse(copy_path).iter(f"{{{MEI_NS}}}incip"))
    copy_bytes = copy_path.read_bytes()
    assert H["class_edition_for_camat"](ctx) == copy_path
    assert copy_path.read_bytes() == copy_bytes
    # The class edition is unchanged and still has its incipit
    assert path.read_bytes() == before
    assert len(list(_parse(path).iter(f"{{{MEI_NS}}}incip"))) == len(incipits)
    # Dynamics per bar in df_events = <dynam> per music measure (ElementTree)
    df_pitch, df_events = _camat_tables(copy_path)
    music = _music_measures(root)
    dyn = df_events[df_events["type"] == "dynamic"]
    by_bar = Counter(str(int(float(m))) for m in dyn["Measure"])
    expected = {n: sum(1 for e in _marks(m) if _name(e) == "dynam") for n, m in music.items()}
    assert by_bar == Counter({n: c for n, c in expected.items() if c})
    # Neighbouring case: the notes table is the same with or without the incipit
    full_pitch, _ = _camat_tables(path)
    assert len(df_pitch) == len(full_pitch)


def _opening_clefs(svg):
    """SMuFL code of the clef that opens each staff in the first measure of an SVG."""
    import xml.etree.ElementTree as ET
    svg_root = ET.fromstring(svg)

    def classes(el):
        return (el.get("class") or "").split()

    measure = next(el for el in svg_root.iter() if "measure" in classes(el))
    codes = []
    for staff in measure:
        if "staff" not in classes(staff):
            continue
        clef = next((c for c in staff if "clef" in classes(c)), None)
        if clef is None:
            codes.append(None)
            continue
        use = clef.find("{http://www.w3.org/2000/svg}use")
        href = use.get("{http://www.w3.org/1999/xlink}href") or use.get("href")
        codes.append(href.lstrip("#")[:4])
    return codes


def test_excerpt_opens_with_clef_in_force(H):
    """Each system opens with the clef in force before it, not the opening scoreDef's.

    E050 = G clef, E062 = F clef. Expected values read from the <clef> changes in the
    reference MEI (left hand treble from bar 1, bass from bar 7, ...).
    """
    import xml.etree.ElementTree as ET
    import verovio
    _need_local_inputs()
    root = _parse(REF_MEI)
    before = ET.tostring(root)
    expected = {
        (1, 4): ["E050", "E062"],    # unchanged: bar 1's own clef change stays in bar 1
        (5, 9): ["E050", "E050"],
        (10, 14): ["E050", "E062"],
        (21, 23): ["E050", "E050"],
        (36, 39): ["E062", "E062"],
    }
    verovio.enableLog(False)
    for (first, last), clefs in expected.items():
        excerpt = H["_excerpt_measures"](root, range(first, last + 1))
        kept = [m.get("n") for m in excerpt.find(f"{{{MEI_NS}}}music").iter(f"{{{MEI_NS}}}measure")]
        assert kept == [str(n) for n in range(first, last + 1)]
        tk = verovio.toolkit()
        tk.setOptions({"breaks": "none", "header": "none", "footer": "none"})
        assert tk.loadData(ET.tostring(excerpt, encoding="unicode"))
        assert _opening_clefs(tk.renderToSVG(1)) == clefs, (first, last)
    assert ET.tostring(root) == before  # the source tree is not touched
