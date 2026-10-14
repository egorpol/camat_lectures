# Changelog

Notable changes to the course materials, newest first. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); entries are dated
instead of versioned, and the date is the day the change went live on the
[site](https://egorpol.github.io/camat_lectures/).

## Unreleased

### Added

- Session 1, part 1: a last tab, *Common notation*, with the melody as Verovio
  renders it from the MEI file.
- Session 1, Demo E: a *Show the bar's MEI* checkbox that shows the selected
  bar's `<measure>` as it is written in the file, with its line numbers.
- Session 1, part 8: a table of the formats with who made them, what for, a
  documentation link and where to find real files.
- Session 1: an addendum on MIDI, as messages on a cable and as a Standard
  MIDI File, with the bytes Verovio writes for the melody.

- Session 1, MIDI addendum: the whole melody as messages on a cable (with
  arrival times) and the whole file, the one-byte clock messages, and why MIDI
  does not simply turn back into MEI.
- Session 1, Demo C and `01_binary_grid.ipynb`: a *Rules* choice between the
  demo's rules (a cell holds what sounds at its start; the grid is read back
  column by column) and CAMAT's (`create_binary_matrix` rounds onsets down and
  ends up; `binary_slice_to_df` reads each row on its own), with messages for
  notes that move to cell edges and for held notes cut by the column reading.

### Changed

- Session 1, part 9: the grid is presented as data computed from a note table,
  as CAMAT uses it for pattern search, and no longer as a model of the piano
  roll. New bullets on what CAMAT does with the grid, with links to its
  `binary_roundtrip` and `binary_pattern_search` notebooks. The SUPRA
  hole-chain numbers moved to Demo A.

- Session 1, part 9 and Demo C: say why `1111` comes back as one whole note
  without the onset grid (a run of 1s is read as one held note, as on a roll)
  and why reading every 1 as a new note is no better.

### Fixed

- Demo A: dragging the speed or start slider no longer makes the slider jump
  under the pointer (the labels next to them changed width as the values
  changed).

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
- `get_notebooks.sh`, a bash version of `get_notebooks.py` for the JupyterLab
  terminal (curl or wget, never overwrites a notebook). The setup page shows
  the two commands that run it.
- Session 1, part 4: the table of notations for human readers links each
  system to a source to look at (the St. Gallen Cantatorium on e-codices, the
  Buxheim Organ Book and Schedel's songbook at the Bayerische Staatsbibliothek,
  pictures on Wikimedia Commons, a jeongganbo encoding paper), and the
  notations made for user groups have a table of their own with an example for
  each.
- Session 1: a "What is Verovio?" box at the top of the page.
- Demo A: a speed slider (0.25× to 2×) that also works while the window plays,
  and a legend entry for loudness.
- Part 9 and Demo C: the sounding and onset grids explained as one grid with
  three values (0 = silence, 1 = a note continues, 2 = a note starts); with the
  onset grid ticked, cells show 2 where a note starts.
- Notebooks: piano rolls can be drawn with matplotlib or Bokeh
  (`BACKEND = "plt"` or `"bokeh"`, or `backend=` per call, as in CAMAT); the
  player-piano notebook gets `speed` for its sound and sliders. When the
  browser cannot draw the sliders, the cell now says what to do instead of
  printing `interactive(children=(...`.
- Session 1, parts 5 and 7: the tables of notation for machines and for
  computers link each row to a source to look at or listen to (Engramelle's
  *La tonotechnie* and Lovelace's Note A on the Internet Archive, photographs
  on Wikimedia Commons, the Banū Mūsā reconstruction at ZKM, the CSIRAC and
  Ferranti recordings, the *Illiac Suite* score, a RISM incipit, and kern,
  Essen and MuseData scores in the Verovio Humdrum Viewer).

### Changed

- Demo A and its notebook: the shade of a note now spans the roll's own
  loudness range (velocity 33 to 85), so soft and loud notes look different;
  before, most notes had nearly the same shade.

### Fixed

- Session 1, part 5: the Banū Mūsā flute player is described in their
  treatise *The Instrument That Plays by Itself*, not in the *Book of
  Ingenious Devices*.
