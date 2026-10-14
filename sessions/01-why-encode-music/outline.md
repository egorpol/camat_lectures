# Session 1 — Why encode music? From notation to machine-readable scores

*Von der digitalen Edition zur computergestützten Musikanalyse: Einführung in Musik-Encoding und Tools für die Notentextanalyse* — session 1, 15 October 2026.

Assumed length: **90 minutes**; shift the times in the plan if the slot differs.
Background notes on historical notation: [historical_music_notation_computational_musicology.md](../../historical_music_notation_computational_musicology.md).
Tested example encodings: [examples/](examples/).

## Core message

Every notation is already an encoding. It was designed for a particular reader and a particular use, and it writes down some things while leaving others to the reader's knowledge. Computers, and now language models, are readers without that knowledge, so music encoding formats must state explicitly what human readers infer. Formats differ for the same reason historical notations differ: they serve different users and tasks.

## Learning goals

By the end of the session, students can:

1. Explain why a score made for human readers is not enough for a computer (implicit knowledge, ambiguity, image vs. data).
2. Ask three questions of any notation or format: *Who reads it? What does it record? What does it leave out?*
3. Place key systems on a timeline from mechanical instruments to kern and the Essen folksong collection, and relate them to today's formats.
4. Recognise a short ABC, kern and MEI snippet and render it with Verovio in Jupyter4NFDI.

## Plan

| Time | Part | Mode |
|---|---|---|
| 0:00–0:10 | 1. Hook: one melody, six encodings | demo + question |
| 0:10–0:25 | 2. Why encode music? | input + discussion |
| 0:25–0:40 | 3. Notation for human readers: systems made for users | input |
| 0:40–0:55 | 4. Notation for machines: barrels, rolls, punched cards | input + **Demo A** (player piano) |
| 0:55–1:10 | 5. Notation for computers, 1940s to the 1990s | input |
| 1:10–1:25 | 6. Today's formats in Verovio | **Demo B** (hands-on if time allows) |
| 1:25–1:30 | 7. Wrap-up, course roadmap, homework | |

If time runs short, cut part 3 to three examples (neumes, tablature, jeongganbo) and skip the hands-on in part 6.

## 1. Hook: one melody, six encodings (10 min)

Show the first four bars of *Alle meine Entchen* as plain text in ABC, kern, Plaine & Easie, EsAC, MusicXML and MEI (all in [examples/](examples/)).

- Ask: *Which of these is the music? Which can you read? Which can a computer read?*
- Then render all six with Verovio: the same score six times.
- Point to the sizes: the same 11 notes take 60 bytes in Plaine & Easie, 75 in ABC, 104 in kern, 1,886 in MusicXML and 4,850 in MEI (as Verovio writes it). The difference is not the notes but what else is recorded: title, metadata, identifiers for every element, layout.
- AI angle: language models read music as text too. ChatMusician (2024) was trained on ABC notation. Optional: ask an LLM to continue the melody in ABC and render its answer with Verovio.

## 2. Why encode music? (15 min)

- **Notation is a selection** made for a reader who knows the conventions: performance practice, tuning, ornament realisation, how repeats work.
- **A computer knows none of this.** A scanned score is an image. For search, analysis, rendering or playback, the machine needs symbols with explicit meaning.
- **Three questions** to ask of every system this semester:
  1. *Who reads it?* A singer, a lutenist, a cataloguer, a machine, a language model.
  2. *What does it record?* Pitch, duration, physical action, sound, structure, layout, metadata.
  3. *What does it leave out,* or leave to the reader?
- **Written vs. performed.** One written sign (a trill, a grace note, a fermata) stands for performed events that differ from what is written. MEI keeps both, for example `@dur` (written duration) next to `@dur.ges` (performed duration).
- **The link to this course.** A digital edition (MEI) encodes what the source says. Analysis (kern, CAMAT tables, piano rolls) treats notes as data. The same encoding has to serve both, which is what the semester is about.

## 3. Notation for human readers: systems made for users (15 min)

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

Forward links to mention: chant is encoded today in GABC and Volpiano (Verovio reads both; see [examples/alleluia_fragment.gabc](examples/alleluia_fragment.gabc)); MEI has a mensural module; jianpu inspired the Essen code in part 5.

## 4. Notation for machines: barrels, rolls, punched cards (15 min)

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

Source: SUPRA (Stanford University Piano Roll Archive), roll `dc920rk8870`.

1. Show the scanned roll in Stanford's viewer: <https://purl.stanford.edu/dc920rk8870>. Link only; image rights stay with Stanford Libraries.
2. In the notebook, download the two MIDI versions at runtime:
   - *raw*: every perforation becomes an event (33,508 note-on events in 6 tracks, 744 s);
   - *expressive*: holes merged into notes and the expression tracks turned into loudness (6,031 notes, 749 s).
3. Plot the first ~20 seconds as a piano roll (time × pitch), the same view CAMAT uses later for its note tables.

Discussion: *Is a roll a score, a recording or a program? Where are the bar lines and the quarter notes? What is a "note" when 33,508 holes become 6,031 notes?*

## 5. Notation for computers, 1940s to the 1990s (15 min)

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

## 6. Today's formats in Verovio (15 min)

Demo B, notebook `01_formats_verovio.ipynb` (to build):

1. Setup on Jupyter4NFDI: `%pip install verovio`.
2. Load each file in [examples/](examples/) and render the SVGs side by side.
3. Compare what each records beyond the notes: phrase marks in EsAC (visible as brackets in the render), spines in kern, `<divisions>` in MusicXML, the header and `xml:id`s in MEI.
4. Convert: kern → MEI with `getMEI()`; MEI → `renderToTimemap()` → piano-roll plot. This links back to Demo A and forward to the CAMAT representations.
5. Hands-on (if time allows): change a note in the ABC and the kern version, add a sharp, then break the syntax on purpose and read the error.

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

## 7. Wrap-up (5 min)

- Recap the three questions: who reads it, what it records, what it leaves out.
- Course roadmap: digital edition (MEI) → CAMAT note tables and piano rolls → statistics and pattern search.
- Homework:
  1. Log in to Jupyter4NFDI (<https://hub.nfdi-jupyter.de>, Helmholtz AAI) and run the Verovio notebook.
  2. Encode the first phrase of a melody of your choice in ABC or kern and render it.
  3. Write down one thing about the melody that your encoding cannot express.

## To prepare before tomorrow

- [x] Example encodings, tested with Verovio 6.3 ([examples/](examples/)).
- [ ] Slides: timeline parts 3–5 (about 15–20 slides).
- [ ] Notebook `01_formats_verovio.ipynb` (Demo B).
- [ ] Notebook `01_player_piano.ipynb` (Demo A): downloads the SUPRA MIDI at runtime; `mido` + `matplotlib`.
- [ ] Run both notebooks once on Jupyter4NFDI.
- [ ] Optional: LLM-writes-ABC demo.

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
