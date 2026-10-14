# Changelog

Notable changes to the course materials, newest first. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); entries are dated
instead of versioned, and the date is the day the change went live on the
[site](https://egorpol.github.io/camat_lectures/).

## Unreleased

## 2026-10-14

### Added

- Live site at <https://egorpol.github.io/camat_lectures/> (MkDocs Material
  on GitHub Pages) with a home page and a setup page for Jupyter4NFDI.
- Session 1, *Why encode music? From notation to machine-readable scores*:
  the page with five demos that run in the browser. Demo A plays Debussy's
  *Children's Corner* roll from SUPRA as raw and expressive MIDI and draws it
  as a piano roll. Demo B renders one melody in six text encodings with
  Verovio. Demo C turns the melody into a 0/1 grid and back. Demo D checks
  melodies an LLM wrote in ABC and kern against the task's rules. Demo E links the zones of a Buxtehude page scan
  to its MEI.
- Three notebooks for session 1 that repeat the demos with inputs to change:
  `01_formats_verovio.ipynb` (Demos B and D), `01_player_piano.ipynb`
  (Demo A) and `01_binary_grid.ipynb` (Demo C). They run in clean Python
  3.10, 3.11 and 3.13 environments.
- `get_notebooks.py` copies the notebooks of all sessions from GitHub into
  `camat_lectures/`, without git, and never overwrites a notebook that is
  already there. The setup page shows the one notebook cell that runs it;
  downloading and uploading from the session page remains the fallback.
- README with the link to the live site, and this changelog.
