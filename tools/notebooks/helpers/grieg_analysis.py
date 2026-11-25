"""Grieg's Vöglein, session 4 block 1: fetch each pair's system and merge the class edition.

Pasted after grieg_linking.py and grieg_editing.py in the same cell; it uses those files'
names (MEI_NS, XML_ID, MARKS, REVIEW_DECISIONS, _bars, _short, _show_picture, _crop,
_read, _name, _text, _pitch, _describe, _places, _read_sheet, _manifest, …).
Helpers must not import each other.
"""

import copy
import csv
import datetime
import http.client
import io
import json
import re
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

NOTE_LIKE = {"note", "chord", "rest", "mRest", "space", "multiRest"}
STRUCTURAL = {"staff", "layer", "beam", "tuplet", "measure", "section", "score",
              "scoreDef", "staffGrp", "staffDef", "layerDef"}
USER_AGENT = "camat-seminar"
FETCH_TIMEOUT = 30
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
REPO_RE = re.compile(
    r"^(?:https://github\.com/)?([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)


# --- Context ----------------------------------------------------------------------

def open_class_folder(start=None):
    """Find the session-3 folder grieg_edition_work and prepare class_edition/."""
    start = Path(start or Path.cwd()).resolve()
    # Fixed candidates only — never walk start.parents (would leave the student's folder).
    candidates = [
        start / "grieg_edition_work",
        (start / "../03-linking-and-editing/grieg_edition_work").resolve(),
        (start / "../../03-linking-and-editing/notebooks/grieg_edition_work").resolve(),
        start / "sessions/03-linking-and-editing/notebooks/grieg_edition_work",
    ]
    project = None
    for candidate in candidates:
        if _class_folder_ok(candidate):
            project = candidate.resolve()
            break
    if project is None:
        raise FileNotFoundError(
            "This notebook needs the folder grieg_edition_work from session 3 "
            "(with inputs/, edition/checkpoints/before-editing.mei and edition/pages/pages.json). "
            "Run 03_grieg_linking.ipynb to the end first, then run this cell again."
        )
    out = project / "class_edition"
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / "fetched").mkdir(exist_ok=True)
    except OSError:
        raise FileNotFoundError(
            f"The session-3 folder was found at {project}, but class_edition/ cannot be created there "
            "(is the folder writable?). Run 03_grieg_linking.ipynb in your own copy, then run this cell again."
        ) from None
    settings = json.loads((project / "inputs/settings.json").read_text(encoding="utf-8"))
    mei_name = settings["mei"]
    mei = project / "inputs" / mei_name
    if not mei.is_file():
        raise FileNotFoundError(
            f"The source encoding inputs/{mei_name} is missing. "
            "Run 03_grieg_linking.ipynb to the end first, then run this cell again."
        )
    before = project / "edition/checkpoints/before-editing.mei"
    pages_json = project / "edition/pages/pages.json"
    sources_path = project / "inputs/sources.json"
    context = {
        "project": project,
        "inputs": project / "inputs",
        "settings": settings,
        "sources": json.loads(sources_path.read_text(encoding="utf-8")) if sources_path.is_file() else {},
        "mei": mei,
        "before": before,
        "work": project / "edition/mei/work.mei",
        "pages_json": pages_json,
        "class_edition": out,
        "class_mei": out / "class-edition.mei",
        "coverage_csv": out / "coverage.csv",
        "layout_systems": _layout_systems(settings["layout"]),
    }
    print("Session-3 folder:", _short(project, project))
    print("Class edition folder:", _short(out, project))
    return context


def _class_folder_ok(path):
    path = Path(path)
    if not path.is_dir():
        return False
    settings_path = path / "inputs/settings.json"
    if not settings_path.is_file():
        return False
    try:
        mei_name = json.loads(settings_path.read_text(encoding="utf-8"))["mei"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return False
    return ((path / "inputs" / mei_name).is_file()
            and (path / "edition/checkpoints/before-editing.mei").is_file()
            and (path / "edition/pages/pages.json").is_file())


def _layout_systems(lines):
    """[(printed_page, system_number, [bar, …]), …] in layout order."""
    from camat.pdf_facsimile import parse_page_layout
    text = "\n".join(lines) if isinstance(lines, (list, tuple)) else str(lines)
    parsed = parse_page_layout(text, page_count=2)
    systems = []
    for pdf_page in sorted(parsed):
        page = parsed[pdf_page]
        printed = str(page.get("printed_page") or "")
        for index, bars in enumerate(page.get("systems", []), 1):
            systems.append((printed, index, [str(b) for b in bars]))
    return systems


def _system_key(page, system):
    return str(page), int(system)


# --- Class list -------------------------------------------------------------------

def read_class_list(text, context):
    """Parse the CSV class list. Returns (rows, picked_by_system). Bad rows are skipped."""
    known = {_system_key(p, s): bars for p, s, bars in context["layout_systems"]}
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        print("✗ The class list is empty. Paste the instructor's list into CLASS_LIST.")
        return [], {}
    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    if reader.fieldnames is None:
        print("✗ The class list has no header. It must start with: page,system,pair,repository,commit,use")
        return [], {}
    required = ["page", "system", "pair", "repository", "commit", "use"]
    fields = [((name or "").strip().lower()) for name in reader.fieldnames]
    if any(name not in fields for name in required):
        print("✗ The class list header must be: page,system,pair,repository,commit,use")
        return [], {}
    rows, by_system = [], defaultdict(list)
    for raw in reader:
        row = {((k or "").strip().lower()): (v or "").strip() for k, v in raw.items() if k is not None}
        page, system = row.get("page", ""), row.get("system", "")
        if not page and not system and not row.get("repository"):
            continue
        key = None
        try:
            key = _system_key(page, system)
        except ValueError:
            print(f"! Skipping a row: page={page!r}, system={system!r} is not a known system.")
            continue
        if key not in known:
            print(f"! Skipping a row: page {page}, system {system} is not in the layout.")
            continue
        owner_repo = _parse_repository(row.get("repository", ""))
        if owner_repo is None:
            print(f"! Skipping page {page}, system {system} ({row.get('pair') or '?'}): "
                  "repository must look like OWNER/REPO or https://github.com/OWNER/REPO.")
            continue
        commit = row.get("commit", "")
        if not COMMIT_RE.fullmatch(commit):
            print(f"! Skipping page {page}, system {system} ({row.get('pair') or '?'}): "
                  "commit must be 7 to 40 hex characters.")
            continue
        use = row.get("use", "").lower()
        if use not in ("", "yes"):
            print(f"! Skipping page {page}, system {system}: use must be 'yes' or empty, not {row.get('use')!r}.")
            continue
        owner, repo = owner_repo
        entry = {
            "page": key[0], "system": key[1], "bars": known[key],
            "pair": row.get("pair") or "?",
            "owner": owner, "repo": repo,
            "repository": f"{owner}/{repo}",
            "commit": commit, "use": use == "yes",
        }
        rows.append(entry)
        by_system[key].append(entry)
    picked = {}
    for key, group in by_system.items():
        if len(group) == 1:
            picked[key] = group[0]
        else:
            marked = [r for r in group if r["use"]]
            if len(marked) == 1:
                picked[key] = marked[0]
            else:
                page, system = key
                print(f"! Page {page}, system {system}: {len(group)} versions, "
                      f"{'none' if not marked else 'several'} marked with use=yes. "
                      "The instructor marks exactly one; this system is not merged.")
    print(f"Class list: {len(rows)} row{'s' if len(rows) != 1 else ''}, "
          f"{len(picked)} system{'s' if len(picked) != 1 else ''} picked for the merge.")
    return rows, picked


def _parse_repository(value):
    value = (value or "").strip()
    found = REPO_RE.fullmatch(value)
    if not found:
        return None
    return found.group(1), found.group(2)


# --- Fetch ------------------------------------------------------------------------

def _cache_dir(context, owner, repo, commit):
    return context["class_edition"] / "fetched" / f"{owner}__{repo}__{commit}"


def _raw_url(owner, repo, commit, relative):
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{relative}"


def _fetch_bytes(url):
    """Return (data, error_message). error_message is None on success."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT) as answer:
            return answer.read(), None
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None, "404"
        return None, f"HTTP {error.code}"
    except (OSError, http.client.HTTPException):
        # URLError, TimeoutError, a reset or a dropped download (IncompleteRead)
        return None, "no connection"


def fetch_pair(context, row, *, relative="mei/work.mei"):
    """Fetch one file for a row into the cache. Returns (path_or_None, status)."""
    cache = _cache_dir(context, row["owner"], row["repo"], row["commit"])
    target = cache / relative
    if target.is_file():
        return target, "cached"
    url = _raw_url(row["owner"], row["repo"], row["commit"], relative)
    data, problem = _fetch_bytes(url)
    if problem == "404":
        return None, "404"
    if problem:
        return None, problem
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target, "fetched"


def fetch_class(context, rows):
    """Fetch work.mei and the review sheet for every class-list row. Updates each row in place."""
    for row in rows:
        mei_path, mei_status = fetch_pair(context, row, relative="mei/work.mei")
        sheet_rel = f"reviews/page-{row['page']}-system-{row['system']}.md"
        sheet_path, sheet_status = fetch_pair(context, row, relative=sheet_rel)
        row["mei_path"] = mei_path
        row["mei_status"] = mei_status
        row["sheet_path"] = sheet_path
        row["sheet_status"] = sheet_status
        label = f"{row['pair']} (page {row['page']}, system {row['system']}, {row['repository']}@{row['commit'][:7]})"
        if mei_status == "404":
            print(f"✗ {label}: work.mei not found at this commit "
                  "(is the repository public, is the commit right?).")
        elif mei_status == "no connection":
            print(f"✗ {label}: no connection. Check the internet and run the cell again.")
        elif mei_status.startswith("HTTP"):
            print(f"✗ {label}: could not fetch work.mei ({mei_status}).")
        elif mei_status == "cached":
            print(f"✓ {label}: work.mei from the cache.")
        else:
            print(f"✓ {label}: fetched work.mei.")
        if sheet_status == "404":
            print(f"  ! no review sheet at reviews/page-{row['page']}-system-{row['system']}.md")
        elif sheet_status == "no connection":
            print(f"  ! review sheet: no connection.")
        elif sheet_status.startswith("HTTP"):
            print(f"  ! review sheet: {sheet_status}.")
        elif sheet_path is not None:
            print(f"  ✓ review sheet ({sheet_status}).")
    return rows


# --- Notes and marks --------------------------------------------------------------

def _music_measure_list(root):
    """Music measures in document order: [(n, element), …]."""
    music = root.find(f"{{{MEI_NS}}}music")
    if music is None:
        return []
    return [(m.get("n"), m) for m in music.iter(f"{{{MEI_NS}}}measure") if m.get("n")]


def _music_measures(root):
    """{n: measure}; if n is repeated, the last wins — notes_equal rejects repeats first."""
    return {n: m for n, m in _music_measure_list(root)}


def _inside_note(element, measure):
    parent_map = {child: parent for parent in measure.iter() for child in parent}
    current = parent_map.get(element)
    while current is not None and current is not measure:
        if _name(current) == "note":
            return True
        current = parent_map.get(current)
    return False


def _accid_key(note):
    values = []
    if note.get("accid"):
        values.append(("accid", note.get("accid")))
    if note.get("accid.ges"):
        values.append(("accid.ges", note.get("accid.ges")))
    for child in note:
        if _name(child) == "accid":
            values.append(("accid-child",
                           tuple(sorted((k, v) for k, v in child.attrib.items() if k != XML_ID)),
                           " ".join((child.text or "").split())))
    return tuple(values)


def _note_key(element):
    """Identity of a note-like element for the notes check."""
    name = _name(element)
    base = (name, element.get(XML_ID) or "",
            element.get("pname") or "", element.get("oct") or "",
            element.get("dur") or "", element.get("dots") or "",
            element.get("grace") or "", _accid_key(element))
    if name == "chord":
        children = tuple(_note_key(n) for n in element if _name(n) == "note")
        return base + (children,)
    return base


def _note_keys_in_measure(measure):
    """Note-like keys in document order; notes inside a chord count only via the chord."""
    keys = []

    def walk(element):
        name = _name(element)
        if name in NOTE_LIKE:
            keys.append(_note_key(element))
            return
        for child in element:
            walk(child)

    for child in measure:
        walk(child)
    return keys


def notes_equal(source_root, other_root):
    """True if music measures' note-like content matches. Else (False, [bar, …])."""
    source_list, other_list = _music_measure_list(source_root), _music_measure_list(other_root)
    source_ns = [n for n, _ in source_list]
    other_ns = [n for n, _ in other_list]

    def _bar_sort_key(n):
        return int(n) if str(n).isdigit() else 0

    involved = []
    for seq in (source_ns, other_ns):
        for n, count in Counter(seq).items():
            if count > 1 and n not in involved:
                involved.append(n)
    if source_ns != other_ns:
        length = max(len(source_ns), len(other_ns))
        for index in range(length):
            a = source_ns[index] if index < len(source_ns) else None
            b = other_ns[index] if index < len(other_ns) else None
            if a != b:
                for n in (a, b):
                    if n is not None and n not in involved:
                        involved.append(n)
        return False, sorted(involved, key=_bar_sort_key) or ["?"]
    if involved:
        return False, sorted(involved, key=_bar_sort_key)

    source, other = _music_measures(source_root), _music_measures(other_root)
    bad = []
    for n in source_ns:
        if _note_keys_in_measure(source[n]) != _note_keys_in_measure(other[n]):
            bad.append(n)
    return (not bad), bad


def _content_key(element):
    """Canonical mark/content key: no xml:id, sorted attributes, normalised text, children."""
    attrs = tuple(sorted((k, v) for k, v in element.attrib.items() if k != XML_ID))
    text = " ".join((element.text or "").split())
    children = tuple(_content_key(child) for child in element)
    return (_name(element), attrs, text, children)


def _mark_start(element):
    return element.get("startid") or element.get("tstamp") or ""


def _marks_in_measure(measure):
    return [e for e in measure.iter()
            if _name(e) in MARKS and e is not measure and not _inside_note(e, measure)]


def _nested_marks(root):
    """Marks that hold another mark, and the marks they hold (not valid MEI): the merge refuses both."""
    found = set()
    for mark in root.iter():
        if _name(mark) in MARKS:
            inner = [e for e in mark.iter() if e is not mark and _name(e) in MARKS]
            if inner:
                found.add(mark)
                found.update(inner)
    return found


def _other_keys_in_measure(measure):
    """Differences that are neither marks nor note-like (ties, artic, …)."""
    mark_tree = set()
    # Marks, and a pair's analysis findings (<annot>, block 2), are not "other changes".
    for mark in _marks_in_measure(measure) + [e for e in measure.iter() if _name(e) == "annot"]:
        for element in mark.iter():
            mark_tree.add(element)
    keys = []
    for element in measure.iter():
        if element is measure or element in mark_tree:
            continue
        name = _name(element)
        if name in NOTE_LIKE or name in STRUCTURAL or name in MARKS or name == "accid":
            continue
        keys.append(_content_key(element))
    return keys


def pair_changes(source_root, pair_root, system_bars):
    """Compare a pair's music marks to the source. system_bars = bars of their own system."""
    source_m, pair_m = _music_measures(source_root), _music_measures(pair_root)
    system_bars = {str(b) for b in system_bars}
    added, removed, changed = [], [], []  # (bar, element [, old_element])
    outside, other = [], []
    for n in sorted(set(source_m) | set(pair_m), key=lambda x: int(x) if str(x).isdigit() else 0):
        s_marks = _marks_in_measure(source_m[n]) if n in source_m else []
        p_marks = _marks_in_measure(pair_m[n]) if n in pair_m else []
        s_counter = Counter(_content_key(e) for e in s_marks)
        p_counter = Counter(_content_key(e) for e in p_marks)
        s_by_key = defaultdict(list)
        p_by_key = defaultdict(list)
        for e in s_marks:
            s_by_key[_content_key(e)].append(e)
        for e in p_marks:
            p_by_key[_content_key(e)].append(e)
        add_els, rem_els = [], []
        for key, count in p_counter.items():
            extra = count - s_counter[key]
            for _ in range(max(0, extra)):
                add_els.append(p_by_key[key].pop())
        for key, count in s_counter.items():
            missing = count - p_counter[key]
            for _ in range(max(0, missing)):
                rem_els.append(s_by_key[key].pop())
        # Pair changed: same kind, staff, start
        used_add, used_rem = set(), set()
        for i, new in enumerate(add_els):
            for j, old in enumerate(rem_els):
                if j in used_rem:
                    continue
                if (_name(new) == _name(old)
                        and (new.get("staff") or "") == (old.get("staff") or "")
                        and _mark_start(new) == _mark_start(old)):
                    used_add.add(i)
                    used_rem.add(j)
                    bucket = changed if n in system_bars else outside
                    if n in system_bars:
                        changed.append((n, new, old))
                    else:
                        outside.append((n, "changed", new, old))
                    break
        for i, new in enumerate(add_els):
            if i in used_add:
                continue
            if n in system_bars:
                added.append((n, new))
            else:
                outside.append((n, "added", new, None))
        for j, old in enumerate(rem_els):
            if j in used_rem:
                continue
            if n in system_bars:
                removed.append((n, old))
            else:
                outside.append((n, "removed", None, old))
        s_other = Counter(_other_keys_in_measure(source_m[n]) if n in source_m else [])
        p_other = Counter(_other_keys_in_measure(pair_m[n]) if n in pair_m else [])
        if s_other != p_other:
            diff = sum((s_other - p_other).values()) + sum((p_other - s_other).values())
            other.append((n, diff))
    return {
        "added": added, "removed": removed, "changed": changed,
        "outside": outside, "other": other,
    }


def _kinds_phrase(items):
    """'slur 1, pedal 1, dynam 1' from a list of elements or (bar, el, …) tuples."""
    names = []
    for item in items:
        el = item[1] if isinstance(item, tuple) else item
        names.append(_name(el))
    counts = Counter(names)
    if not counts:
        return ""
    return ", ".join(f"{name} {counts[name]}" for name in sorted(counts))


def _review_summary(sheet_path):
    if sheet_path is None or not Path(sheet_path).is_file():
        return "none"
    entries = _read_sheet(Path(sheet_path).read_text(encoding="utf-8"))
    if not entries:
        return "none"

    def word(value):
        return value.split()[0].lower().strip(".,;:!") if value.split() else ""

    decided = [c for c, v in entries.items() if word(v) in REVIEW_DECISIONS]
    not_readable = [c for c, v in entries.items() if v and word(v) not in REVIEW_DECISIONS]
    empty = [c for c, v in entries.items() if not v]
    counts = ", ".join(f"{n} {w}" for w in REVIEW_DECISIONS
                       if (n := sum(word(entries[c]) == w for c in decided)))
    parts = [f"{len(decided)} of {len(entries)} decided"]
    if counts:
        parts[0] += f": {counts}"
    if not_readable:
        parts.append(f"{len(not_readable)} not readable")
    if empty:
        parts.append(f"{len(empty)} empty")
    return "; ".join(parts)


# --- Merge ------------------------------------------------------------------------

def _all_ids(root):
    ids = {}
    duplicates = set()
    for element in root.iter():
        i = element.get(XML_ID)
        if not i:
            continue
        if i in ids:
            duplicates.add(i)
        ids[i] = element
    return ids, duplicates


def _fresh_xml_id(base_id, page, system, ids):
    """A unique xml:id derived from base_id for page/system; append -2, -3, … if needed."""
    candidate = f"{base_id}-p{page}s{system}"
    if candidate not in ids:
        return candidate
    number = 2
    while f"{candidate}-{number}" in ids:
        number += 1
    return f"{candidate}-{number}"


def _pointers_ok(element, ids):
    for attr in ("startid", "endid", "plist"):
        for token in (element.get(attr) or "").split():
            target = token.lstrip("#")
            if target and target not in ids:
                return False
    return True


def _same_start_conflict(measure, element):
    """True if measure already has a mark of same kind/staff/start but different content."""
    key = _content_key(element)
    for other in _marks_in_measure(measure):
        if other is element:
            continue
        if (_name(other) == _name(element)
                and (other.get("staff") or "") == (element.get("staff") or "")
                and _mark_start(other) == _mark_start(element)
                and _content_key(other) != key):
            return True
    return False


def _find_mark_by_key(measure, key):
    for element in _marks_in_measure(measure):
        if _content_key(element) == key:
            return element
    return None


def _append_mark(measure, element):
    measure.append(element)


def _remove_mark(measure, element):
    # element may be from another tree; find by content key
    key = _content_key(element)
    found = _find_mark_by_key(measure, key)
    if found is not None:
        measure.remove(found)
        return True
    return False


def build_class_edition(context, rows, picked):
    """Merge picked systems into class_edition/class-edition.mei and write coverage.csv."""
    source = _read(context["mei"])
    base = _read(context["before"])
    if source is None or base is None:
        return None
    ok, bad = notes_equal(source, base)
    if not ok:
        print(f"✗ The file before editing differs in its notes from the source encoding "
              f"(bars {', '.join(bad)}). Stop and re-run session 3 linking.")
        return None

    analyses = {}  # id(row) or key → analysis dict
    row_status = {}  # system key → status details for coverage

    for row in rows:
        key = _system_key(row["page"], row["system"])
        info = {
            "row": row, "status": None, "changes": None, "notes_bad": [],
            "messages": [], "merged": False,
        }
        if row.get("mei_path") is None:
            info["status"] = "not fetched"
            analyses[id(row)] = info
            continue
        root = _read(row["mei_path"])
        if root is None:
            info["status"] = "not XML"
            analyses[id(row)] = info
            continue
        ok, bad = notes_equal(source, root)
        if not ok:
            info["status"] = "notes differ"
            info["notes_bad"] = bad
            print(f"! {row['pair']} (page {row['page']}, system {row['system']}): "
                  f"notes differ in bar{'s' if len(bad) != 1 else ''} {', '.join(bad)}; not merged.")
            analyses[id(row)] = info
            continue
        changes = pair_changes(source, root, row["bars"])
        info["changes"] = changes
        info["root"] = root
        info["status"] = "ready"
        analyses[id(row)] = info
        outside_n = len(changes["outside"])
        if outside_n:
            print(f"  {row['pair']}: {outside_n} change{'s' if outside_n != 1 else ''} "
                  "outside its system, not copied.")
        other_n = sum(n for _, n in changes["other"])
        if other_n:
            bars = ", ".join(b for b, _ in changes["other"])
            print(f"  {row['pair']}: {other_n} other change{'s' if other_n != 1 else ''} "
                  f"(bars {bars}), not copied.")

    # Merge in layout order
    edition = copy.deepcopy(base)
    measures = _music_measures(edition)
    ids, _ = _all_ids(edition)
    merge_log = []  # (page, system, repository, commit)
    refused_messages = []

    for page, system, bars in context["layout_systems"]:
        key = _system_key(page, system)
        group = [r for r in rows if _system_key(r["page"], r["system"]) == key]
        if not group:
            row_status[key] = {"status": "gap: no pair", "row": None, "analysis": None,
                               "others": 0}
            continue
        if key not in picked:
            row_status[key] = {"status": "several versions, none picked", "row": None,
                               "analysis": None, "others": len(group)}
            continue
        chosen = picked[key]
        info = analyses[id(chosen)]
        others = len(group) - 1
        if info["status"] == "not fetched":
            row_status[key] = {"status": "not fetched", "row": chosen, "analysis": info,
                               "others": others}
            continue
        if info["status"] == "not XML":
            row_status[key] = {"status": "not XML", "row": chosen, "analysis": info,
                               "others": others}
            continue
        if info["status"] == "notes differ":
            row_status[key] = {"status": "notes differ", "row": chosen, "analysis": info,
                               "others": others}
            continue

        changes = info["changes"]
        # Count only what reaches the class edition; every refusal adds one message.
        applied = {"added": [], "changed": [], "removed": []}
        first_refusal = len(refused_messages)
        nested = _nested_marks(info["root"])
        nested_note = "a mark inside another mark is not valid MEI."
        # Removals
        for bar, old in changes["removed"]:
            measure = measures.get(bar)
            if measure is None:
                continue
            if _remove_mark(measure, old):
                applied["removed"].append((bar, old))
            else:
                refused_messages.append(
                    f"! Could not remove <{_name(old)}> in bar {bar} from the class edition."
                )
        # Changes: replace old content with new
        for bar, new, old in changes["changed"]:
            measure = measures.get(bar)
            if measure is None:
                continue
            if new in nested:
                refused_messages.append(f"✗ Refused a changed <{_name(new)}> in bar {bar}: {nested_note}")
                continue
            if not _pointers_ok(new, ids):
                refused_messages.append(
                    f"✗ Refused a changed <{_name(new)}> in bar {bar}: "
                    "a startid/endid/plist points to no element in the class edition."
                )
                continue
            found = _find_mark_by_key(measure, _content_key(old))
            if found is None:
                refused_messages.append(
                    f"! Could not apply a change to <{_name(old)}> in bar {bar}."
                )
                continue
            # Replace attributes and text; keep/replace xml:id carefully
            for attr in list(found.attrib):
                if attr != XML_ID:
                    del found.attrib[attr]
            for attr, value in new.attrib.items():
                if attr == XML_ID:
                    continue
                found.set(attr, value)
            found.text = new.text
            for child in list(found):
                found.remove(child)
            for child in new:
                found.append(copy.deepcopy(child))
            new_id = new.get(XML_ID)
            if new_id:
                if new_id in ids and ids[new_id] is not found:
                    renamed = _fresh_xml_id(new_id, page, system, ids)
                    old_id = found.get(XML_ID)
                    if old_id and old_id in ids and ids[old_id] is found:
                        del ids[old_id]
                    found.set(XML_ID, renamed)
                    ids[renamed] = found
                    print(f"  ! Renamed xml:id {new_id} → {renamed} (already in the class edition).")
                else:
                    found.set(XML_ID, new_id)
                    ids[new_id] = found
            applied["changed"].append((bar, new, old))
        # Additions
        for bar, new in changes["added"]:
            measure = measures.get(bar)
            if measure is None:
                continue
            if new in nested:
                refused_messages.append(f"✗ Refused a <{_name(new)}> in bar {bar}: {nested_note}")
                continue
            key_content = _content_key(new)
            if _find_mark_by_key(measure, key_content) is not None:
                refused_messages.append(
                    f"✗ Refused a duplicate <{_name(new)}> in bar {bar} "
                    f"({_text(new) or 'no text'}): the class edition already has this mark."
                )
                continue
            # Also refuse if source/base already has it (same as above on measure)
            probe_ids = dict(ids)
            if not _pointers_ok(new, probe_ids):
                refused_messages.append(
                    f"✗ Refused a <{_name(new)}> in bar {bar}: "
                    "a startid/endid/plist points to no element in the class edition."
                )
                continue
            clone = copy.deepcopy(new)
            new_id = clone.get(XML_ID)
            if new_id and new_id in ids:
                renamed = _fresh_xml_id(new_id, page, system, ids)
                clone.set(XML_ID, renamed)
                print(f"  ! Renamed xml:id {new_id} → {renamed} (already in the class edition).")
                new_id = renamed
            if new_id:
                ids[new_id] = clone
            if _same_start_conflict(measure, clone):
                print(f"  ! Warning: bar {bar} already has a <{_name(clone)}> on the same staff "
                      f"and start with different content; both are kept.")
            _append_mark(measure, clone)
            applied["added"].append((bar, clone))

        info["merged"] = True
        info["applied"] = applied
        info["refused"] = len(refused_messages) - first_refusal
        merge_log.append((page, system, chosen["repository"], chosen["commit"]))
        row_status[key] = {"status": "merged", "row": chosen, "analysis": info, "others": others}
        refused_note = f"; {info['refused']} refused" if info["refused"] else ""
        print(f"✓ Merged page {page}, system {system} from {chosen['repository']}@{chosen['commit'][:7]} "
              f"({_kinds_phrase(applied['added']) or 'no additions'}"
              f"{'; ' + _kinds_phrase(applied['changed']) + ' changed' if applied['changed'] else ''}"
              f"{'; ' + _kinds_phrase(applied['removed']) + ' removed' if applied['removed'] else ''}"
              f"{refused_note}).")

    for message in refused_messages:
        print(message)

    # Rewrite graphic targets for class_edition/
    for graphic in edition.iter(f"{{{MEI_NS}}}graphic"):
        target = graphic.get("target") or ""
        name = Path(target).name
        if name:
            graphic.set("target", f"../edition/pages/{name}")

    # revisionDesc change
    m = f"{{{MEI_NS}}}"
    head = edition.find(f"{m}meiHead")
    revision = head.find(f"{m}revisionDesc") if head is not None else None
    if head is not None and revision is None:
        revision = ET.SubElement(head, f"{m}revisionDesc")
    if revision is not None:
        existing = revision.findall(f"{m}change")
        number = max((int(c.get("n")) for c in existing if (c.get("n") or "").isdigit()), default=0) + 1
        change = ET.SubElement(revision, f"{m}change", {"n": str(number)})
        desc = ET.SubElement(change, f"{m}changeDesc")
        if merge_log:
            parts = [f"page {p}, system {s} from {repo}@{commit}"
                     for p, s, repo, commit in merge_log]
            text = ("Class edition: merged " + "; ".join(parts) + ".")
        else:
            text = "Class edition: no systems merged."
        p = ET.SubElement(desc, f"{m}p")
        p.text = text
        date = ET.SubElement(change, f"{m}date", {"isodate": datetime.date.today().isoformat()})

    ET.register_namespace("", MEI_NS)
    out_path = context["class_mei"]
    tree = ET.ElementTree(edition)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    # Ensure trailing newline for stable bytes
    data = out_path.read_bytes()
    if not data.endswith(b"\n"):
        out_path.write_bytes(data + b"\n")

    coverage = _build_coverage(context, rows, picked, row_status, analyses)
    coverage.to_csv(context["coverage_csv"], index=False)
    context["coverage"] = coverage
    context["rows"] = rows
    context["picked"] = picked
    context["row_status"] = row_status
    context["analyses"] = analyses

    # Summary line
    merged_keys = [k for k, v in row_status.items() if v["status"] == "merged"]
    covered_bars = []
    for page, system, bars in context["layout_systems"]:
        if _system_key(page, system) in merged_keys:
            covered_bars.extend(bars)
    print(f"\nWrote {_short(out_path, context['project'])} and "
          f"{_short(context['coverage_csv'], context['project'])}.")
    if covered_bars:
        print(f"Covered: {len(merged_keys)} system{'s' if len(merged_keys) != 1 else ''}, "
              f"{_bars(covered_bars)}.")
    else:
        print("Covered: no systems merged yet.")
    print("A complete review sheet can still hold unresolved entries: it is not proof that the marks are right.")
    print("Coverage counts each pair's changes against the source, not every mark in the file "
          "(the source already has *p*, *pp*, staccato dots and accents).")
    return coverage


def _build_coverage(context, rows, picked, row_status, analyses):
    records = []
    for page, system, bars in context["layout_systems"]:
        key = _system_key(page, system)
        info = row_status.get(key, {"status": "gap: no pair", "row": None, "analysis": None, "others": 0})
        row = info.get("row")
        analysis = info.get("analysis")
        changes = (analysis or {}).get("changes")
        applied = (analysis or {}).get("applied")  # set only for a merged system
        status = info["status"]
        record = {
            "page": page,
            "system": system,
            "bars": f"{bars[0]}-{bars[-1]}" if len(bars) > 1 else bars[0],
            "pair": row["pair"] if row else "",
            "commit": (row["commit"][:7] if row else ""),
            "status": status,
            "marks_added": _kinds_phrase(applied["added"]) if applied else "",
            "marks_changed": _kinds_phrase(applied["changed"]) if applied else "",
            "marks_removed": _kinds_phrase(applied["removed"]) if applied else "",
            "refused": (analysis or {}).get("refused", 0),
            "outside": len(changes["outside"]) if changes else 0,
            "other_changes": sum(n for _, n in changes["other"]) if changes else 0,
            "review_sheet": _review_summary(row.get("sheet_path") if row else None),
            "other_versions": info.get("others", 0),
        }
        records.append(record)
    return pd.DataFrame.from_records(records)


def show_coverage(context):
    """Show the coverage table as a DataFrame (and remind how to read it)."""
    coverage = context.get("coverage")
    if coverage is None and context["coverage_csv"].is_file():
        coverage = pd.read_csv(context["coverage_csv"])
        context["coverage"] = coverage
    if coverage is None:
        print("Build the class edition first.")
        return None
    display(coverage)
    return coverage


# --- Other versions ---------------------------------------------------------------

def compare_other_versions(context):
    """For each system with several fetched versions, list mark differences vs the picked one."""
    rows = context.get("rows") or []
    picked = context.get("picked") or {}
    analyses = context.get("analyses") or {}
    source = _read(context["mei"])
    if source is None:
        return
    any_shown = False
    for page, system, bars in context["layout_systems"]:
        key = _system_key(page, system)
        group = [r for r in rows if _system_key(r["page"], r["system"]) == key]
        if len(group) < 2 or key not in picked:
            continue
        chosen = picked[key]
        chosen_info = analyses.get(id(chosen))
        if not chosen_info or chosen_info.get("status") != "ready" and not chosen_info.get("merged"):
            if not chosen_info or chosen_info.get("changes") is None:
                continue
        any_shown = True
        print(f"Page {page}, system {system} ({_bars(bars)}), picked: {chosen['pair']}")
        chosen_marks = _system_mark_map(chosen_info["root"], bars)
        by_id = {e.get(XML_ID): e for e in chosen_info["root"].iter() if e.get(XML_ID)}
        place = _places(chosen_info["root"])
        for other in group:
            if other is chosen:
                continue
            other_info = analyses.get(id(other))
            label = f"  vs {other['pair']} ({other['repository']}@{other['commit'][:7]})"
            if not other_info or other_info.get("root") is None:
                print(f"{label}: not available for comparison.")
                continue
            other_marks = _system_mark_map(other_info["root"], bars)
            only_picked = set(chosen_marks) - set(other_marks)
            only_other = set(other_marks) - set(chosen_marks)
            if not only_picked and not only_other:
                print(f"{label}: the same marks")
                continue
            print(label + ":")
            for mark_key in sorted(only_picked, key=lambda t: (int(t[1]), str(t[0]))):
                element = chosen_marks[mark_key]
                print(f"    only in the picked version (bar {mark_key[1]}): "
                      f"{_describe(element, by_id, place)}")
            other_by_id = {e.get(XML_ID): e for e in other_info["root"].iter() if e.get(XML_ID)}
            other_place = _places(other_info["root"])
            for mark_key in sorted(only_other, key=lambda t: (int(t[1]), str(t[0]))):
                element = other_marks[mark_key]
                print(f"    only in {other['pair']} (bar {mark_key[1]}): "
                      f"{_describe(element, other_by_id, other_place)}")
    if not any_shown:
        print("No system has several fetched versions to compare yet.")


def _system_mark_map(root, bars):
    """{(content_key, bar): element} for marks in the given bars."""
    measures = _music_measures(root)
    result = {}
    for bar in bars:
        measure = measures.get(str(bar))
        if measure is None:
            continue
        for element in _marks_in_measure(measure):
            result[(_content_key(element), str(bar))] = element
    return result


# --- Show one system --------------------------------------------------------------

def show_class_system(context, page, system):
    """Render one system of the class edition with Verovio, beside the print crop."""
    import verovio
    from IPython.display import HTML, display as idisplay

    key = _system_key(page, system)
    known = {_system_key(p, s): bars for p, s, bars in context["layout_systems"]}
    if key not in known:
        print(f"Page {page}, system {system} is not in the layout.")
        return
    bars = known[key]
    path = context["class_mei"]
    if not path.is_file():
        print("Build the class edition first.")
        return
    root = _read(path)
    if root is None:
        return
    excerpt = _excerpt_measures(root, bars)
    verovio.enableLog(False)
    tk = verovio.toolkit()
    tk.setOptions({
        "scale": 40,
        "adjustPageHeight": True,
        "header": "none",
        "footer": "none",
        "breaks": "auto",
        "pageWidth": 1800,
        "pageMarginTop": 40,
        "pageMarginBottom": 40,
        "pageMarginLeft": 40,
        "pageMarginRight": 40,
        "mnumInterval": 1,
    })
    xml = ET.tostring(excerpt, encoding="unicode")
    if not xml.lstrip().startswith("<?xml"):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml
    if not tk.loadData(xml):
        print("✗ Verovio could not draw this system.")
        return
    for number in range(1, tk.getPageCount() + 1):
        svg = tk.renderToSVG(number)
        idisplay(HTML(f'<div style="background:white; padding:4px; overflow-x:auto">{svg}</div>'))
    print(f"Class edition, page {page}, system {system}, {_bars(bars)} (MEI bar numbers).")
    # Print crop from the student's before-editing links
    try:
        boxes = _boxes(context)
        image = boxes[bars[0]][0]
        union = (min(boxes[b][1][0] for b in bars), min(boxes[b][1][1] for b in bars),
                 max(boxes[b][1][2] for b in bars), max(boxes[b][1][3] for b in bars))
        labels = [(boxes[b][1][0] + 30, union[1] + 10, f"bar {b}") for b in bars]
        print("The same bars in the print:")
        _crop(image, union, labels)
    except Exception as problem:
        print(f"! Could not show the print crop ({problem}).")


_CLEF_ATTRS = ("shape", "line", "dis", "dis.place")


def _clefs_before(music, bars):
    """{staff n: {attr: value}}: the clef in force just before the first bar in bars.

    Reads staffDef clefs and <clef> changes inside staves, in document order.
    """
    state = {}

    def walk(element, staff_n):
        if element.tag == f"{{{MEI_NS}}}measure" and element.get("n") in bars:
            return True
        if element.tag == f"{{{MEI_NS}}}staffDef":
            child = element.find(f"{{{MEI_NS}}}clef")
            if child is not None:
                state[element.get("n")] = {a: child.get(a) for a in _CLEF_ATTRS if child.get(a)}
            elif element.get("clef.shape"):
                state[element.get("n")] = {a: element.get(f"clef.{a}") for a in _CLEF_ATTRS
                                           if element.get(f"clef.{a}")}
            return False
        if element.tag == f"{{{MEI_NS}}}staff":
            staff_n = element.get("n")
        if element.tag == f"{{{MEI_NS}}}clef" and staff_n is not None and element.get("shape"):
            state[staff_n] = {a: element.get(a) for a in _CLEF_ATTRS if element.get(a)}
        return any(walk(child, staff_n) for child in element)

    walk(music, None)
    return state


def _excerpt_measures(root, bars):
    """A shallow MEI document with only the named measures (for Verovio).

    Each staff opens with the clef in force before the first kept bar: the hands
    change clef inside bars, so the opening scoreDef's clefs are often wrong.
    """
    bars = {str(b) for b in bars}
    excerpt = copy.deepcopy(root)
    music = excerpt.find(f"{{{MEI_NS}}}music")
    clefs = _clefs_before(music, bars)
    parents = {child: parent for parent in music.iter() for child in parent}
    for measure in list(music.iter(f"{{{MEI_NS}}}measure")):
        if measure.get("n") not in bars:
            parents[measure].remove(measure)
    score_def = next(music.iter(f"{{{MEI_NS}}}scoreDef"), None)
    if score_def is not None:
        for staff_def in score_def.iter(f"{{{MEI_NS}}}staffDef"):
            clef = clefs.get(staff_def.get("n"))
            if not clef:
                continue
            child = staff_def.find(f"{{{MEI_NS}}}clef")
            for a in _CLEF_ATTRS:
                staff_def.attrib.pop(f"clef.{a}", None)
                if child is not None:
                    child.attrib.pop(a, None)
            for a, value in clef.items():
                if child is not None:
                    child.set(a, value)
                else:
                    staff_def.set(f"clef.{a}", value)
    # drop facsimile: not needed for rendering notes
    for facs in list(music.findall(f"{{{MEI_NS}}}facsimile")):
        music.remove(facs)
    return excerpt


# --- Statistics -------------------------------------------------------------------

def class_edition_for_camat(context):
    """Write an analysis copy without the header incipit and return its path.

    CAMAT's event table also reads the incipit's own bars 1 and 2, so bar 1 would get
    a second p. The class edition itself keeps its incipit.
    """
    path = context["class_mei"]
    if not path.is_file():
        print("Skipped. Build the class edition first.")
        return None
    root = _read(path)
    if root is None:
        return None
    for parent in root.iter():
        for incipit in parent.findall(f"{{{MEI_NS}}}incip"):
            parent.remove(incipit)
    ET.register_namespace("", MEI_NS)
    copy_path = path.parent / "for_camat" / path.name
    copy_path.parent.mkdir(exist_ok=True)
    ET.ElementTree(root).write(copy_path, encoding="utf-8", xml_declaration=True)
    return copy_path


def _measure_label(value):
    """Normalise a df_events Measure value to the MEI bar-number string."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        text = str(value).strip()
        return text or None


def plot_marks_per_bar(context, df_events):
    """Marks per bar from df_events (not tie, clef, artic, measure); shade uncovered systems."""
    import matplotlib.pyplot as plt
    if df_events is None:
        print("Skipped. Read the class edition into CAMAT first.")
        return None
    path = context.get("class_mei")
    root = _read(path) if path and Path(path).is_file() else None
    if root is None:
        print("Skipped. Build the class edition first.")
        return None
    bar_nums = [n for n, _ in _music_measure_list(root)]
    skip = {"tie", "clef", "artic", "measure", "rest"}
    marks = df_events[~df_events["type"].isin(skip)].copy()
    marks["_bar"] = marks["Measure"].map(_measure_label)
    marks = marks[marks["_bar"].notna()]
    if marks.empty:
        types = []
        pivot = pd.DataFrame(index=bar_nums)
    else:
        pivot = marks.groupby(["_bar", "type"]).size().unstack(fill_value=0)
        pivot = pivot.reindex(bar_nums, fill_value=0)
        types = list(pivot.columns)
    fig, ax = plt.subplots(figsize=(11, 4))
    x = list(range(len(bar_nums)))
    bottom = [0] * len(bar_nums)
    for typ in types:
        vals = [int(pivot.loc[bar, typ]) if typ in pivot.columns else 0 for bar in bar_nums]
        ax.bar(x, vals, bottom=bottom, width=0.85, label=typ)
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_xticks(x)
    ax.set_xticklabels(bar_nums)
    uncovered = []
    status = context.get("row_status") or {}
    pos = {bar: index for index, bar in enumerate(bar_nums)}
    for page, system, bars in context["layout_systems"]:
        key = _system_key(page, system)
        info = status.get(key)
        if not info or info.get("status") != "merged":
            for bar in bars:
                uncovered.append(bar)
                if bar in pos:
                    index = pos[bar]
                    ax.axvspan(index - 0.5, index + 0.5, color="#cccccc", alpha=0.35, zorder=0)
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Bar (MEI)")
    ax.set_ylabel("Marks")
    ax.set_title("Marks per bar (from who restored what)")
    if types:
        ax.legend(title="type", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    plt.show()
    print("Counts follow who restored what, not the music alone. "
          "Shaded bars belong to systems that were not merged into the class edition.")
    if uncovered:
        print(f"Uncovered bars: {_bars([str(b) for b in sorted(set(uncovered), key=lambda n: int(n) if str(n).isdigit() else 0)])}.")
    return ax
