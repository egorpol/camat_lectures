# Changelog

Notable changes to the course materials, newest first. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); entries are dated
instead of versioned, and the date is the day the change went live on the
[site](https://egorpol.github.io/camat_lectures/).

## Unreleased

## 2026-10-27

### Changed

- Session 2: *What is SVG?* is now a page of the site, opened from session 2's
  *What is SVG?* box, in the site's light and dark modes. Its pickup note is
  drawn live from our starting file; highlighting it adds `fill` and `color`
  to the note's SVG text, while the MEI stays the same.

### Removed

- Sessions 3 and 4: the overview pages are off the site until they are
  revised after session 2.
- Instructor material (outlines, answer keys, preparation notes and the tools
  that need them) and the drafts for sessions 3 and 4 are out of the
  repository for now; the site no longer serves the unlinked session 3/4
  example files.

### Added

- *Setup on your laptop*: a step-by-step page, done together in class, for
  VS Code, Miniforge with the `seminar` environment (Python 3.12, Poppler,
  CAMAT 0.2.8), Git, GitHub and Copilot, with a check after each step.
- *Setup on Jupyter4NFDI*: a cloud route from session 2 on, for students
  without a laptop: a Jupyter4NFDI workshop with the seminar's packages
  (`binder/environment.yml`, same pins as the laptop), the notebooks in the
  kept folder `work`, a first look at mei-friend, and a do-it-yourself
  environment as fallback. Session 2 shows *Laptop* and *Cloud* tabs where the
  steps differ.
- Session 2, *Building an edition: the source and the notes*: laptop setup;
  source, scan, encoding and edition; a wrong note in the reused Schumann MEI
  (A3 for F3), found by OMR; recorded OMR results next to the scan; five notes
  in ABC; the page and its bars, with one table from musicians' bar numbers to
  MEI numbers, systems and IDs. Notebooks `02_pdf_preparation`,
  `02_schumann_omr` and `02_note_entry`, with their data ZIPs.
- Session 2 page demos: the pickup and bar 1, and bar 5, from the MEI Sample
  Collection file next to our starting file, with the wrong note in blue; an
  ABC box for the pickup and bar 1 that renders as you type and lists the
  notes Verovio read, bar by bar.
- Session 2, part 4: what HOMR and OeMeR are and how they work, Audiveris as
  an OMR program with a correction window, and HOMR's demo website. Part 5:
  *Two more ways in*, MuseScore and a language model, and an *Any format* box
  that reads ABC, MEI, MusicXML, kern or Plaine & Easie, pasted or opened from
  a file, and shows the result as MEI.
- Session 2, part 7: click a note or rest in the pickup and bar 1 of our
  starting file to see its pitch and length, its tag in the MEI file and the
  SVG group Verovio drew for it, with the same `xml:id`; a short *What is SVG?*
  box links the SVG introduction. The instructor outline has an optional
  demo in which Copilot compares HOMR's MusicXML with our MEI.
- Sessions 3 and 4: overview pages for linking and editing, and for
  publishing and first analysis.
- The notebook downloaders also copy the data ZIPs that notebooks need.
- Session-file publishing leaves out notebook runtime folders, so locally
  downloaded scans never reach the course site.

### Changed

- Session 2 page: the box "What is MEI?" is gone (session 1 covers it).
- Session 2 notebooks rewritten in session 1's plain voice, with one core path
  and marked extensions; no minute ranges or hashes in student text.
  `02_schumann_omr` shows the scan of the first two systems (downloaded once,
  shared with `02_pdf_preparation`) above HOMR's result, and lists a bar in
  words by musicians' bar numbers; "What we found" is collapsed. Its old claim
  of an extra F4 in HOMR's two-system result was wrong (that F4 is in the
  full-page run). Corrected after checking against the recorded data: the A3 is
  in the MEI Sample Collection file, not in our starting file; HOMR gets every
  note of the two systems right and leaves out beams; most misplaced slurs come
  from Verovio's import of HOMR's file, not from HOMR; OeMeR reads most of the
  right hand in the bass clef. The rendered OMR scores no longer show Verovio's
  bar numbers, which count the pickup as bar 1. `02_note_entry` gives only
  header and pickup in ABC, checks the typed notes against the print, and
  collapses the solution; its *Verovio reads* lists rests too, as on the page,
  and the check says when bar 1 lacks its closing `|]`. The other formats are
  extensions without route letters. `02_pdf_preparation` prints the bar table
  (bar, MEI `n`, system, `xml:id`); its download and check errors say in plain
  words what to do.

## 2026-10-15

### Added

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
- Session 1, Demo C and `01_binary_grid.ipynb`: under CAMAT's rules the
  *keep an onset grid* box is greyed out, because CAMAT has no onset layer
  yet; CAMAT's read-back always joins a run of 1s into one note, as its
  `binary_slice_to_df` does.

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

### Changed

- Demo A and its notebook: the shade of a note now spans the roll's own
  loudness range (velocity 33 to 85), so soft and loud notes look different;
  before, most notes had nearly the same shade.
- Session 1, part 9 and Demo C: say why `1111` comes back as one whole note
  without the onset grid (a run of 1s is read as one held note, as on a roll)
  and why reading every 1 as a new note is no better.

### Fixed

- Session 1, part 5: the Banū Mūsā flute player is described in their
  treatise *The Instrument That Plays by Itself*, not in the *Book of
  Ingenious Devices*.
- Demo A: dragging the speed or start slider no longer makes the slider jump
  under the pointer (the labels next to them changed width as the values
  changed).
