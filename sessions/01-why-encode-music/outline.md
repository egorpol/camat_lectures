# Session 1 — Why encode music? From notation to machine-readable scores

*Von der digitalen Edition zur computergestützten Musikanalyse: Einführung in Musik-Encoding und Tools für die Notentextanalyse* — session 1, 15 October 2026.

Format: **double session, 2 × 90 minutes**, with about 30 minutes reserved for technical setup (Jupyter4NFDI login).
Materials: a **live page** (GitHub Pages; served locally for now) carries the content and in-browser demos; **notebooks** on Jupyter4NFDI carry the same demos with inputs students can change (see [Live page and notebooks](#live-page-and-notebooks)).
Background notes on historical notation: [historical_music_notation_computational_musicology.md](../../historical_music_notation_computational_musicology.md).
Tested example encodings: [examples/](examples/).

## Core message

Every notation is already an encoding. It was designed for a particular reader and a particular use, and it writes down some things while leaving others to the reader's knowledge. Computers, and now language models, are readers without that knowledge, so music encoding formats must state explicitly what human readers infer. Formats differ for the same reason historical notations differ: they serve different users and tasks.

## Learning goals

By the end of the session, students can:

1. Explain why a score made for human readers is not enough for a computer (implicit knowledge, ambiguity, image vs. data).
2. Ask three questions of any notation or format: *Who reads it? What does it record? What does it leave out?*
3. Place key systems on a timeline from mechanical instruments to kern and the Essen folksong collection, and relate them to today's formats.
4. Edit a short ABC, kern or MEI snippet and render it with Verovio, in the browser and in Jupyter4NFDI.
5. Turn a melody into a 0/1 pitch × time grid and say what the grid loses.
6. Tell a scan, a PDF, an encoded score and a facsimile-linked edition apart, and say who can use each (including readers who cannot see the page).
7. Check an LLM-written ABC melody against what was asked for.

## Plan

**Block 1 — concepts and history (90 min)**

| Time | Part | Mode |
|---|---|---|
| 0:00–0:10 | 1. Hook: one melody, seven encodings | live page + question |
| 0:10–0:20 | 2. Why encode music? | input + discussion |
| 0:20–0:35 | 3. Scores today: scans, PDFs and facsimile-based editions | input + showcase: eu-pd-composers, **Demo E** (facsimile preview) |
| 0:35–0:45 | 4. Notation for human readers: systems made for users | input (three examples) |
| 0:45–1:00 | 5. Notation for machines: barrels, rolls, punched cards | input + **Demo A** on the live page (player piano) |
| 1:00–1:30 | 6. Setup: Jupyter4NFDI login and first notebook | hands-on troubleshooting |

Setup goes at the end of block 1 so the break absorbs overruns and block 2 starts with everyone logged in. Students who are still stuck can follow block 2 on the live page, which needs no login.

**Block 2 — encodings hands-on (90 min)**

| Time | Part | Mode |
|---|---|---|
| 0:00–0:20 | 7. Notation for computers, 1940s to the 1990s | input |
| 0:20–0:45 | 8. Today's formats in Verovio | **Demo B**, students edit inputs |
| 0:45–1:05 | 9. Binary notation: holes, grids and what survives | **Demo C**, preview of CAMAT |
| 1:05–1:20 | 10. An LLM writes ABC | **Demo D** |
| 1:20–1:30 | 11. Wrap-up, course roadmap, homework | |

Part 3 was added on 2026-10-14 (user's request); to make room, part 2 went from 15 to 10 minutes, part 4 uses the three-example version (neumes, tablature, jeongganbo; the other systems stay on the live page for reading) and part 5 went from 20 to 15 minutes. If time still runs short, shorten part 7 to the table.

## Live page and notebooks

Every demo exists twice: on the live page (runs in any browser, nothing to install) and as a notebook (students change inputs, rerun, keep their work).

| Demo | Live page | Notebook (Jupyter4NFDI) |
|---|---|---|
| A. Player-piano roll | piano roll of Debussy's roll, MIDI fetched at runtime | `01_player_piano.ipynb`: raw vs. expressive MIDI, zoom, choose a passage |
| B. Seven encodings | one editable text box per format, rendered by Verovio | `01_formats_verovio.ipynb`: edit, render, convert to MEI |
| C. Binary grid | melody → 0/1 grid → notes, grid size adjustable | `01_binary_grid.ipynb`: change the melody and the resolution, compare before/after |
| D. LLM writes ABC | paste box + recorded LLM answers | cells at the end of `01_formats_verovio.ipynb` |
| E. Facsimile-linked edition (part 3, showcase only) | one DdT page: Verovio rendering next to the BSB scan (IIIF, fetched at runtime) with its measure zones | none in session 1; the full workflow comes with CAMAT later |

Checked on 2026-10-14:

- **Verovio in the browser works.** Verovio 6.3.0 is on npm and jsdelivr serves `verovio-toolkit-wasm.js` (HTTP 200). That is the same version as the Python wheel, so page and notebook render alike.
- **A static page cannot call an LLM** without an API key, hence the paste box and recorded answers.
- **CAMAT already has matching pieces** in `camat_v2/notebooks/`: an interactive MEI editor and renderer (`mei_render.ipynb`, `launch_interactive_mei_renderer`), and binary grids and piano rolls (`binary_roundtrip.ipynb`, `binary_pattern_search.ipynb`; `create_binary_matrix_bundle`, `draw_piano_roll`, `binary_matrix_designer`).

Decided (2026-10-14): the live page is built with MkDocs Material, with custom JavaScript blocks for the Verovio demos and notebooks offered as downloads. Session 1's notebooks use plain Verovio (`verovio`, `mido`, `matplotlib`, `ipywidgets`); CAMAT comes in from session 2.

## 1. Hook: one melody, seven encodings (10 min)

Show the first four bars of *Alle meine Entchen* as plain text in ABC, kern, Plaine & Easie, EsAC, MusicXML and MEI (all in [examples/](examples/)), plus a seventh, purely binary version: one row per pitch, one column per quarter note, 1 = sounding.

```
      bar 1   bar 2   bar 3   bar 4
A4    0000    0000    1111    0000
G4    0000    1111    0000    1111
F4    0001    0000    0000    0000
E4    0010    0000    0000    0000
D4    0100    0000    0000    0000
C4    1000    0000    0000    0000
```

- Ask: *Which of these is the music? Which can you read? Which can a computer read?*
- Then render the six text formats with Verovio: the same score six times. Keep the grid for part 9: it cannot be rendered back into this score without guessing.
- Point to the sizes: the same 11 notes take 60 bytes in Plaine & Easie, 75 in ABC, 104 in kern, 1,886 in MusicXML and about 4,850 in MEI (as Verovio writes it; its random IDs change the length by a few bytes each time). The difference is not the notes but what else is recorded: title, metadata, identifiers for every element, layout.
- AI angle: language models read music as text too. ChatMusician (2024) was trained on ABC notation. Part 10 comes back to this.

## 2. Why encode music? (10 min)

- **Notation is a selection** made for a reader who knows the conventions: performance practice, tuning, ornament realisation, how repeats work.
- **A computer knows none of this.** A scanned score is an image. For search, analysis, rendering or playback, the machine needs symbols with explicit meaning.
- **Three questions** to ask of every system this semester:
  1. *Who reads it?* A singer, a lutenist, a cataloguer, a machine, a language model.
  2. *What does it record?* Pitch, duration, physical action, sound, structure, layout, metadata.
  3. *What does it leave out,* or leave to the reader?
- **Written vs. performed.** One written sign (a trill, a grace note, a fermata) stands for performed events that differ from what is written. MEI keeps both, for example `@dur` (written duration) next to `@dur.ges` (performed duration).
- **The link to this course.** A digital edition (MEI) encodes what the source says. Analysis (kern, CAMAT tables, piano rolls) treats notes as data. The same encoding has to serve both, which is what the semester is about.

## 3. Scores today: scans, PDFs and facsimile-based editions (15 min)

Added on 2026-10-14. Answers "why encode?" from what students meet today, and prefaces CAMAT's facsimile-based editions.

- **Where scores live today.** Library digitisations (for example the Bayerische Staatsbibliothek's digital collections, delivered as IIIF images), PDF archives such as IMSLP, publishers' editions, and a few encoded editions in MEI. Most "digital" music is a picture of a page.
- **Formats of digitised archives.** Image files (TIFF, JPEG) behind a IIIF viewer; PDFs (a container of page images, at most with a text layer, never with the music as data); encoded scores (MusicXML, MEI, kern). Only the last can be searched for a melody, played, transposed or analysed.
- **Access: who may use it.** Rights depend on the composer's death year (EU: life + 70 years), on the edition and on the country. Showcase: the eu-pd-composers viewer (<https://egorpol.github.io/eu-pd-composers/>), which lists 20th-century composers whose music is likely public domain in the EU, with IMSLP links. Numbers on the live page are from the deployed viewer, dump r019 (checked 2026-10-14): 3,369 composers; 777 PD now, 1,870 not yet, 722 without death date; 21 more on 1 January 2027; 1,254 IMSLP matches; 29,033 work pages, 20,391 by PD-now composers. The checkout's README (r020, branch `feat/open-licence-sweep`) gives the same values. Repeat its "not legal advice" note. In-class prompt: whose music becomes free on 1 January 2027?
- **Accessibility: who can use it.** A scan cannot be read aloud by a screen reader, enlarged without blur, played back or turned into music Braille; an encoding can (link to music Braille in part 4).
- **Facsimile-based editions.** MEI keeps the page images in `<facsimile>` (one `<surface>` per page, one `<zone>` per measure), and each `measure/@facs` points to its zone. The encoding stays tied to its source: every bar can be checked against the page, the source's page and system breaks are kept, and the editor's reading sits next to the witness. A traditional critical edition replaces the source with a new engraving and moves the differences into a critical report.
- **CAMAT preview.** CAMAT's edition tools grew out of encoding volumes of *Denkmäler deutscher Tonkunst* (DdT): page-level OMR from musiconn.scoresearch, BSB IIIF facsimiles, correction in mei-friend, automatic checks. A second route links MEI to the pages of a PDF (developed on Webern's *Variations*, Op. 27, Universal Edition print of 1937: nine pages, 143 measure regions). See CAMAT's guides "Editing music with the MEI data format" and "Link MEI to a PDF facsimile".
- **Demo E (showcase only).** Page 1 of Buxtehude's Sonata I, Op. I (DdT 11, p. 3, BSB image 00013; bars 1–15), cut from the published `DdT_1_vol_11` (commit `7af4ae8`) with `tools/extract_facsimile_page.py` into `examples/facsimile/`. The scan with its 15 zones next to Verovio's rendering (encoded breaks: 3 systems as in the print); point at or click a bar on either side; the selected bar is shown close up (IIIF crop of the zone and Verovio's rendering of that bar alone). Bar 11 carries the page's one editorial `<annot>` (C♯ eighth instead of DdT's sixteenth, after the first edition). Its text says "the 1696 print", but Op. I is usually dated about 1694 (Op. II 1696); the live page caveats this. The full workflow comes later in the course.
- **Discussion:** *Is a facsimile-linked encoding more authentic than a clean modern edition? Authentic to what: the source, the work, the performance?*

## 4. Notation for human readers: systems made for users (10 min)

Short, one slide each, using the "who / what / left out / computational analogy" grid from the background notes:

| System | Encodes | Computational analogy |
|---|---|---|
| Greek alphabetic notation (Seikilos epitaph) | symbols mapped to pitches | lookup table |
| Neumes (9th century onward) | melodic contour, often without fixed pitch | relative constraints |
| Guidonian hand, staff lines | pitch as a position in space | spatial lookup |
| Mensural notation | duration depends on context | rule engine |
| Lute and organ tablature | where to put the fingers, not which pitch | instrument instruction set |
| Jeongganbo (Korea, 15th century onward) | time as a grid of cells | temporal grid, close to a piano roll |

One slide on **notations customised for a user group**: shape notes (singing schools), jianpu (scale degrees as numbers, for teaching), music Braille (blind musicians), Klavarskribo (keyboard players). There was never one "music notation"; systems are tools built for a use, and encoding formats continue that tradition.

Forward links to mention: chant is encoded today in GABC and Volpiano (Verovio reads both; see [examples/alleluia_fragment.gabc](examples/alleluia_fragment.gabc)); MEI has a mensural module; jianpu inspired the Essen code in part 7.

## 5. Notation for machines: barrels, rolls, punched cards (15 min)

When the reader is a machine, notation becomes a program: positions on a cylinder or holes in paper that trigger sound.

| When | What | Point for the seminar |
|---|---|---|
| 9th century, Baghdad | Banū Mūsā, *Book of Ingenious Devices*: automatic flute player driven by a rotating pinned cylinder | often called an early programmable machine (popular claim; present it with care) |
| 17th century onward | pinned barrels in barrel organs and music boxes | music stored as physical positions |
| 1801–1804 | Jacquard loom: punched cards control weaving patterns | not music, but punched cards become the medium of music machines and computers |
| 1843 | Ada Lovelace's Notes on the Analytical Engine: if the relations of pitched sounds could be expressed in symbols, the engine "might compose elaborate and scientific pieces of music of any degree of complexity or extent" | the encoding problem, stated before computers existed |
| 1890s | Edwin Votey's piano-player mechanism, sold by Aeolian as the Pianola (1897) | mass-market executable notation |
| 1904 | Welte-Mignon reproducing piano (Edwin Welte and Karl Bockisch, Freiburg; public launch 1905) | records tempo, dynamics and pedalling, not only notes |
| 1908 | Buffalo meeting of US manufacturers: 88-note roll standard (9 holes per inch) | a format standard, so any roll plays on any instrument |
| from 1948 | Conlon Nancarrow punches his *Studies for Player Piano* by hand | the roll as a composition medium for music no human can play |

### Demo A: Debussy plays *Children's Corner* (Welte-Mignon roll 2733)

Source: SUPRA (Stanford University Piano Roll Archive), roll `dc920rk8870`. Shown on the live page; students repeat it in `01_player_piano.ipynb` in block 2 or at home.

1. Show the scanned roll in Stanford's viewer: <https://purl.stanford.edu/dc920rk8870>. Link only; image rights stay with Stanford Libraries.
2. In the notebook, download the two MIDI versions at runtime:
   - *raw*: every perforation becomes an event (33,508 note-on events in 6 tracks, 744 s);
   - *expressive*: holes merged into notes and the expression tracks turned into loudness (6,031 notes, 749 s).
3. Plot the first ~20 seconds as a piano roll (time × pitch), the same view CAMAT uses later for its note tables.

Discussion: *Is a roll a score, a recording or a program? Where are the bar lines and the quarter notes? What is a "note" when 33,508 holes become 6,031 notes?*

## 6. Setup: Jupyter4NFDI login and first notebook (30 min)

1. Open <https://hub.nfdi-jupyter.de>, sign in with Helmholtz AAI and start JupyterLab on JSC-Cloud (steps as in the CAMAT cloud guide).
2. Check the kernel: Python 3.10 or later.
3. Get the session notebooks into the workspace (download from the live page or clone the course repository; to decide).
4. Run the setup cell (`%pip install ...`) and the first render cell. A rendered score is the success check.
5. Collect each problem and its fix; they go into a FAQ on the live page for later sessions.

Files under `/home/jovyan` persist after a restart; everything else is discarded when the server stops.

## 7. Notation for computers, 1940s to the 1990s (20 min)

| When | System | People | Made for | Today |
|---|---|---|---|---|
| 1940s | punched cards for *Barbara Allen* tune variants | Bertrand Bronson | sorting folk tunes into families | folk song as the first computational corpus |
| 1950–1951 | CSIRAC (Australia) plays tunes; Ferranti Mark 1 recorded by the BBC in 1951 | Christopher Strachey (Ferranti) | computers *play* music | no CSIRAC recording survives; it was reconstructed |
| 1957 | *Illiac Suite* for string quartet | Lejaren Hiller, Leonard Isaacson | computers *compose* | the output was transcribed into a score by hand |
| 1960s | DARMS (Ford-Columbia Music Representation) | Stefan Bauer-Mengelberg | computer-printed parts for the New York Philharmonic; entered by counting lines and spaces | historical; pip Verovio 6.3 lacks DARMS, so show it as text |
| 1964 | Plaine & Easie Code | Barry S. Brook, Murray Gould | incipits typed on an ordinary typewriter | RISM adopted it for incipits in the 1970s; still in use, and Verovio renders it |
| from 1982 | EsAC and the Essen Folksong Collection | Helmut Schaffrath | folksongs on DOS PCs; pitches as scale degrees, inspired by jianpu | 8,473 songs in the KernScores listing; Verovio reads EsAC |
| 1983 | MIDI | instrument makers | performance events between instruments, not notation | the piano roll's descendant: note on/off and velocity |
| 1984 | CCARH and MuseData | Walter Hewlett | large encoded repertories | MuseData files still on the CCARH sites |
| 1980s–1990s | Humdrum toolkit and `**kern` | David Huron | analysis with Unix text tools, one column ("spine") per voice; *kern* = German "core" | Essen collection available in kern; Verovio reads Humdrum; used in this course |
| 1980s–1990s | ABC | Chris Walshaw | folk tunes typed as letters (`abc2mtex` by 1993) | the text format behind LLM music models such as ChatMusician (2024) |

Message: the 1960s needed music for **printing** (DARMS) and **cataloguing** (Plaine & Easie). The 1980s brought **corpora for analysis** (Essen, MuseData, kern). Folk song made the first large data sets because monophonic melodies were simple enough to encode at scale.

One bridge slide after 1990: MEI (Perry Roland's XML schema, 1999, built on the principles of TEI) for editions; MusicXML (Recordare, from 2000) for exchange between notation programs; Verovio renders MEI and the other formats in the browser and in Python; language models trained on ABC and kern (2024–).

## 8. Today's formats in Verovio (25 min)

Demo B: first on the live page, then in `01_formats_verovio.ipynb`:

1. Setup on Jupyter4NFDI: `%pip install verovio`.
2. Load each file in [examples/](examples/) and render the SVGs side by side.
3. Compare what each records beyond the notes: phrase marks in EsAC (visible as brackets in the render), spines in kern, `<divisions>` in MusicXML, the header and `xml:id`s in MEI.
4. Convert: kern → MEI with `getMEI()`; MEI → `renderToTimemap()` → piano-roll plot. This links back to Demo A and forward to the CAMAT representations.
5. Hands-on: change a note in the ABC and the kern version, add a sharp, change the metre, then break the syntax on purpose and read the error.

Verovio 6.3 (the pip wheel) input formats as tested on 2026-10-14:

| Format | Verovio `inputFrom` | Tested |
|---|---|---|
| Humdrum `**kern` | `humdrum` | loads, 11 notes correct |
| ABC | `abc` | loads, 11 notes correct |
| Plaine & Easie | `pae` | loads, 11 notes correct |
| EsAC | `esac` | loads, 11 notes correct; needs a header line before `CUT[...]` (prints two harmless warnings) |
| MusicXML | `xml` | loads, 11 notes correct |
| MEI | `mei` | loads, 11 notes correct |
| GABC (chant) | `gabc` | loads; headers are not parsed, so the file starts at the first neume |
| Volpiano (chant) | `volpiano` | loads (tested in a probe, no example file) |
| CMME (mensural) | `cmme.xml` | listed, not tested |
| DARMS | `darms` | "not supported in this build" |

Re-run the check on any machine with `python examples/check_examples.py`.

Found while building the live page (2026-10-14, Verovio 6.3.0, Python wheel and npm build alike unless noted):

- **Browser build:** the default `verovio-toolkit-wasm.js` returns `false` for kern and EsAC; the page uses the Humdrum build `verovio-module-hum.mjs` (12.4 MB) with `verovio.mjs`.
- **Inputs that crash Verovio** (segfault in Python, so the kernel dies; a catchable exception in WASM): ABC without an `X:` line (`T:t\nK:C\nCDEF|`), ABC without a `K:` line, ABC with a `]` that closes nothing (`X:1\nK:C\nCD]EF|`), and kern whose lines have fewer columns than spines (`**kern\t**kern\n4c\t4e\n4d\n*-\t*-`, abort). Page and notebooks check for these before calling Verovio.
- **kern key signatures:** with `*k[f#c#]`, the token `4f#` becomes `<note pname="f"/>` without `accid.ges`, so `getMIDIValuesForElement()` and `renderToMIDI()` give F natural (65 instead of 66). ABC writes `accid.ges` and is correct. The demos compute pitches from the MEI instead (accid.ges, accid, accidental earlier in the bar, key signature).
- **ABC chord lengths:** a length after the bracket is ignored, `[DFA]4` becomes an eighth-note chord with `L:1/8`; `[D4F4A4]` works. The page warns about it.
- **Logs:** in WASM, `enableLogToBuffer(true, module)` makes `getLog()` return the warnings; the Python wheel has no such switch and writes them to stderr, which Jupyter does not show.

## 9. Binary notation: holes, grids and what survives (20 min)

Demo C, a preview of the CAMAT representations used later in the course.

- **Back to the roll.** A perforation is binary: hole or no hole at a position. The raw SUPRA file is exactly that, 33,508 hole events.
- **The melody as a grid** (from part 1):

```
      bar 1   bar 2   bar 3   bar 4
A4    0000    0000    1111    0000
G4    0000    1111    0000    1111
F4    0001    0000    0000    0000
E4    0010    0000    0000    0000
D4    0100    0000    0000    0000
C4    1000    0000    0000    0000
```

- *Which bars can you no longer tell apart?* Bar 2 (two half notes), bar 3 (four quarter notes) and bar 4 (one whole note) all become a run of four cells. Pure occupancy loses where one note ends and the next begins. CAMAT's `binary_roundtrip.ipynb` shows the same effect: adjacent note events form a single run.
- **Resolution is a choice.** A quarter-note grid cannot hold eighth notes; CAMAT's default cell is a sixteenth (0.25 quarter lengths). Finer grids cost size.
- **What would fix it?** A separate onset grid, or keeping the note table next to the grid, as CAMAT does with `xml:id`s pointing back to the score.
- Hands-on: change the melody and the grid size, convert grid → notes → Verovio, and compare with the original.

## 10. An LLM writes ABC (15 min)

Demo D.

- **Why ABC:** compact text with many tune collections online, so language models have seen a lot of it. ChatMusician (2024) was trained on ABC.
- **Live:** ask an LLM on the projector for a short melody in ABC (given key, metre, length), then the same in kern. Paste both into the live page or the notebook and render them.
- **Check:** does every bar add up to the metre? Does Verovio warn? Are key and range what was asked for? Is the kern valid at all?
- **Recorded answers** on the live page keep the demo working without network or LLM access.
- **Data protection:** students do not need their own LLM account; the instructor's demo (or a university service, if available) is enough.
- **Discussion:** the model writes text that looks like music. Because it is an encoding, we can check it, which a picture of a score would not allow.

## 11. Wrap-up (10 min)

- Recap the three questions: who reads it, what it records, what it leaves out. Apply them to the scan, the grid and the LLM's ABC.
- Course roadmap: digital edition (MEI) → CAMAT note tables and piano rolls → statistics and pattern search.
- Homework:
  1. If setup failed in class, finish it with the FAQ on the live page and run `01_formats_verovio.ipynb`.
  2. Encode the first phrase of a melody of your choice in ABC or kern and render it.
  3. Write down one thing about the melody that your encoding cannot express.

## To prepare before tomorrow

- [x] Example encodings, tested with Verovio 6.3 ([examples/](examples/)).
- [x] Live page: session text + demos A–D (served locally first).
- [x] Part 3: eu-pd-composers showcase and Demo E (facsimile preview).
- [x] Notebooks `01_formats_verovio.ipynb`, `01_player_piano.ipynb`, `01_binary_grid.ipynb`.
- [x] Recorded LLM answers (ABC and kern) for Demo D.
- [ ] Run all notebooks once on Jupyter4NFDI.
- [ ] Slides for parts 2–4 and 6, or present them from the live page.

Rights: SUPRA MIDI files are CC BY-NC-SA 4.0 according to the GitHub `LICENSE.txt` (the Stanford Digital Repository record for SUPRA-RW 1.1 says 3.0). Attribute them and cite Shi, Sapp, Arul, McBride and Smith, "SUPRA: Digitizing the Stanford University Piano Roll Archive", ISMIR 2019. Download the MIDI in the notebook rather than committing it. Don't put roll images in this repository; link to Stanford's viewer.

## Dates that need care on slides

- **DARMS:** conception dated 1961 (Wikipedia) or 1966 (CCARH wiki); funding given as 1964–1976. Use "1960s".
- **88-note standard:** most sources say Buffalo, December 1908; some give 1910 or 1911.
- **Humdrum:** "1980s" in some sources, "1990s" in others; the toolkit was reviewed in *Music Theory Online* in 1996.
- **Illiac Suite:** usually 1957; one source names a 1956 premiere.
- **Bronson:** the punched-card study is dated "1940s" in the source found; the original article's title and year are not confirmed.
- **Lovelace:** quote wording varies between transcriptions ("or extent" / "and extent"); check against a scan before putting it on a slide.
- **Banū Mūsā:** "first programmable machine" is a popular claim, not a consensus.

## Sources

- Background notes: [historical_music_notation_computational_musicology.md](../../historical_music_notation_computational_musicology.md)
- DARMS: [Wikipedia](https://en.wikipedia.org/wiki/DARMS_notation), [CCARH wiki](https://wiki.ccarh.org/wiki/DARMS)
- Plaine & Easie: [Wikipedia](https://en.wikipedia.org/wiki/Plaine_%26_Easie_Code), [IAML](https://www.iaml.info/node/469), [TEI/MEC 2023 talk](https://teimec2023.uni-paderborn.de/contributions/114.html)
- EsAC and Essen: [CCARH wiki: ESAC](https://wiki.ccarh.org/wiki/ESAC), [esac-data.org](https://esac-data.org/), [KernScores data collections](https://kernscores.stanford.edu/help/data)
- Humdrum: [Wild, review in *Music Theory Online* 2.7 (1996)](https://mtosmt.org/issues/mto.96.2.7/mto.96.2.7.wild.html)
- ABC: [abcnotation.com history](https://abcnotation.com/history)
- MuseData / CCARH: [CCARH wiki: MuseData](https://wiki.ccarh.org/wiki/MuseData), [ccarh.org](https://ccarh.org/)
- MEI: [music-encoding.org/about](https://music-encoding.org/about); MusicXML: [Good, "MusicXML: The First Decade"](https://michaelgood.info/publications/music/musicxml-the-first-decade/)
- Early computer music: [Computer music (Wikipedia)](https://en.wikipedia.org/wiki/Computer_music), [CSIRAC music (University of Melbourne)](https://cis.unimelb.edu.au/about/csirac/music), [Ferranti Mark 1](https://en.wikipedia.org/wiki/Ferranti_Mark_1), [Illiac Suite](https://en.wikipedia.org/wiki/Illiac_Suite)
- Player pianos: [Piano roll (Wikipedia)](https://en.wikipedia.org/wiki/Piano_roll), [Welte-Mignon](https://en.wikipedia.org/wiki/Welte-Mignon), [Welte patents (Uni Freiburg)](https://welte.ub.uni-freiburg.de/wiki/patente_zum_welte-reproduktionspiano_welte-mignon), [Nancarrow edition project (Paul Sacher Stiftung)](https://www.paul-sacher-stiftung.ch/en/research/1-2-Conlon-Nancarrow-Edition-project.html)
- SUPRA: [supra.stanford.edu](https://supra.stanford.edu/download), [GitHub pianoroll/SUPRA](https://github.com/pianoroll/SUPRA), [SUPRA-RW 1.1 (SDR)](https://purl.stanford.edu/xf457dx9166), [Debussy roll](https://purl.stanford.edu/dc920rk8870)
- Banū Mūsā: [ZKM reconstruction](https://zkm.de/en/node/62659)
- Lovelace: [Computer History Museum](https://www.computerhistory.org/babbage/adalovelace/)
- Bronson: [Bibliolore](https://bibliolore.org/tag/jean-ritchie)
- ChatMusician: [arXiv 2402.16153](https://arxiv.org/abs/2402.16153)
