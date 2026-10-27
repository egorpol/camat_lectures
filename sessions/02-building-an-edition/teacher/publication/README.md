# Publication rehearsal and account-free Git example

Prepared 26 October 2026 with fresh PyPI CAMAT 0.2.8, Verovio 6.3.0, pypdf
6.10.0 and Python 3.11.16. [checks.json](checks.json) records executed local
checks; the [reference notebook](../references/02_review_and_release_recorded.ipynb)
preserves the review/export/build run. Neither creates human source approval.

The [Git bundle](../references/publication/schumann-classroom-example.bundle)
is a portable, account-free repository with two real **scratch demonstration**
commits and a local `v0.1.0` tag. It is not a pushed repository, GitHub release
or public deployment. It contains the linked starter, six prepared changes,
review-stage validation evidence, source instructions and the complete build
template, with no scan files. The example review stays `not_reviewed`.

From a separate working directory, clone the bundle by its actual local path:

```sh
git clone -b main /absolute/path/to/schumann-classroom-example.bundle schumann-git-demo
cd schumann-git-demo
git log --oneline
git diff main~1 main -- mei/work.mei review.json
python -m pip install -r requirements.txt
python scripts/check_edition.py --without-local-images
python scripts/build_site.py
python -m http.server --bind 127.0.0.1 --directory _site 8000
```

Open `http://127.0.0.1:8000/#landmann/1`, `/6` and `/21` (retain the full
`#landmann/` prefix when entering another label). Use `SOURCE.md` to recover
the one-page PDF and open it in the viewer. Regenerating local PNGs for full
resource checks uses the seminar PDF-preparation notebook/settings. The scoped
check above leaves CAMAT's raw conformance failed/incomplete because images
are absent; it still rejects broken IDs or unexpected missing files.

For a visible **uncommitted** diff during the Git primer, inside this disposable
clone only:

```sh
git switch -c classroom-demo main~1
git restore --source main -- mei/work.mei review.json
git diff -- mei/work.mei
```

Students can now stage and commit the small editorial step. Configure their
own Git name/email before class; the two bundled commits use a clearly labelled
classroom identity. The bundle's `origin` is a local file, not a GitHub remote.
Do not push to it expecting a Pages deployment. A real class repository/remote
and its permission setup are a separate instructor preflight.

Verified locally: full checks with images, byte-identical downloadable MEI,
correct clean Git commit/tag identity, fresh-clone build, rejection of broken
internal references and missing images under full validation, deterministic
source-excerpt reconstruction, and preservation on repeated export. Browser
checks cover PDF opening, labels 1/6/21 and note anchors. The actual mei-friend
Schumann import/save test was stopped by declined browser upload approval;
the local structural-checker probes do not substitute for that test.

Before teaching, rehearse source/alignment approval, student frontends and
accounts, one provider request if used, mei-friend save/reopen, and the actual
GitHub push/Pages URL. The session's complete timed classroom run remains an
instructor check.
