# 1. Why encode music? From notation to machine-readable scores

Session 1, 15 October 2026 (double session, 2 × 90 minutes).

Every notation is already an encoding. It was made for a particular reader and a particular use, and it writes down some things while leaving others to the reader's knowledge. Computers, and now language models, are readers without that knowledge, so music encoding formats must state explicitly what human readers infer. Formats differ for the same reason historical notations differ: they serve different users and tasks.

!!! tip "How to use this page"
    The demos on this page run in your browser; nothing needs to be installed. They load [Verovio](https://www.verovio.org) (about 12 MB) the first time you use them. The same demos come as Jupyter notebooks, where you can change the inputs and keep your work: see [Notebooks](#notebooks) at the end.

**By the end of the session you can**

1. explain why a score made for human readers is not enough for a computer;
2. ask three questions of any notation or format: *Who reads it? What does it record? What does it leave out?*;
3. tell a scan, a PDF, an encoded score and a facsimile-linked edition apart, and say who can use each;
4. place key systems on a timeline from mechanical instruments to kern and the Essen folksong collection;
5. edit a short ABC, kern or MEI text and render it with Verovio;
6. turn a melody into a 0/1 grid and say what the grid loses;
7. check an LLM-written melody against what was asked for.

## 1. One melody, seven encodings

Here are the first four bars of *Alle meine Entchen*, seven times. Before anything is rendered: *Which of these is the music? Which can you read? Which can a computer read?*

=== "ABC"

    ```text
    --8<-- "sessions/01-why-encode-music/examples/alle_meine_entchen.abc"
    ```

=== "kern"

    ```text
    --8<-- "sessions/01-why-encode-music/examples/alle_meine_entchen.krn"
    ```

=== "Plaine & Easie"

    ```text
    --8<-- "sessions/01-why-encode-music/examples/alle_meine_entchen.pae"
    ```

=== "EsAC"

    ```text
    --8<-- "sessions/01-why-encode-music/examples/alle_meine_entchen.esac"
    ```

=== "MusicXML"

    ```xml
    --8<-- "sessions/01-why-encode-music/examples/alle_meine_entchen.musicxml"
    ```

=== "MEI"

    ```xml
    --8<-- "sessions/01-why-encode-music/examples/alle_meine_entchen.mei"
    ```

=== "0/1 grid"

    One row per pitch, one column per quarter note, 1 = the pitch sounds.

    ```text
          bar 1   bar 2   bar 3   bar 4
    A4    0000    0000    1111    0000
    G4    0000    1111    0000    1111
    F4    0001    0000    0000    0000
    E4    0010    0000    0000    0000
    D4    0100    0000    0000    0000
    C4    1000    0000    0000    0000
    ```

The same 11 notes take 60 bytes in Plaine & Easie, 75 in ABC, 104 in kern, 120 in EsAC, 1,886 in MusicXML and about 4,850 in MEI (as Verovio writes it; its random IDs change the length by a few bytes each time). The difference is not the notes but what else is recorded: title, metadata, an identifier for every element, layout. Six of the seven can be rendered back into the same score ([part 8](#8-todays-formats-in-verovio)). The grid cannot, at least not without guessing ([part 9](#9-binary-notation-holes-grids-and-what-survives)).

Language models read music as text too: ChatMusician (2024) was trained on ABC ([part 10](#10-an-llm-writes-abc)).

## 2. Why encode music?

- **Notation is a selection** made for a reader who knows the conventions: performance practice, tuning, how to realise an ornament, how repeats work.
- **A computer knows none of this.** A scanned score is an image. To search, analyse, render or play music, a machine needs symbols with explicit meaning.
- **Written and performed differ.** One written sign (a trill, a grace note, a fermata) stands for performed events that look different from what is written. MEI can keep both, for example `@dur` (written duration) next to `@dur.ges` (performed duration).
- **Three questions** to ask of every system this semester:
    1. *Who reads it?* A singer, a lutenist, a cataloguer, a machine, a language model.
    2. *What does it record?* Pitch, duration, physical action, sound, structure, layout, metadata.
    3. *What does it leave out,* or leave to the reader?

A digital edition (MEI) encodes what a source says. Analysis (kern, note tables, piano rolls) treats notes as data. The same encoding has to serve both, and that is what this course is about.

## 3. Scores today: scans, PDFs and facsimile-based editions

**Where do you meet scores today?** In library digitisations (for example the [digital collections of the Bayerische Staatsbibliothek](https://www.digitale-sammlungen.de)), in PDF archives such as [IMSLP](https://imslp.org), in publishers' editions, and in a few encoded editions. Most "digital" music is a picture of a page.

| Form | What the computer has | You can… | You cannot… |
|---|---|---|---|
| Scan (TIFF, JPEG; often served through a [IIIF](https://iiif.io) viewer) | pixels | zoom, compare sources, cite a page | search for a melody, play it, transpose it |
| PDF | page images in a container, at most a text layer | download, print, share | the same as a scan: the notes are still pictures |
| Encoded score (MusicXML, MEI, kern) | symbols with meaning | render, play, search, analyse | see what the source looked like, unless it is linked |
| Facsimile-linked edition (MEI with `<facsimile>`) | symbols *and* the page images, linked bar by bar | all of the above, and check every bar against the source | — |

**Access: who may use a score?** That depends on rights: in the EU, a composer's works are free 70 years after the end of the year of their death, but an edition, an arrangement or a lyricist can still be protected, and countries differ.

!!! example "Showcase: the eu-pd-composers viewer"
    The [eu-pd-composers viewer](https://egorpol.github.io/eu-pd-composers/) ([data and code on GitHub](https://github.com/egorpol/eu-pd-composers)) applies the EU rule to the 3,369 composers on Wikipedia's *List of 20th-century classical composers*, with life dates from Wikidata:

    - 777 are public domain in the EU now (they died in 1955 or earlier), 1,870 are not yet, and 722 have no death date on record. 21 more follow on 1 January 2027.
    - 1,254 are matched to their IMSLP category, with links to 29,033 IMSLP work pages; 20,391 of those pages belong to composers who are public domain now.
    - You can filter by instrumentation, style, citizenship, popularity and the year the works become free.

    *Figures from the published viewer (dump r019, checked on 2026-10-14).* The status is a heuristic based on the composer's death year only, not legal advice: it cannot see lyricists, editions, arrangements or posthumous publications. Check the work itself before you copy, perform or publish it.

    *Try it:* whose music becomes free in the EU on 1 January 2027? Does IMSLP have scores of it?

**Accessibility: who can use a score?** A screen reader cannot read a scan aloud, a scan blurs when enlarged, and it cannot be turned into music Braille or played back. An encoded score can be all of these (music Braille comes up again in [part 4](#4-notation-for-human-readers-systems-made-for-users)).

**Facsimile-based editions** keep the source and the encoding together. MEI stores the page images in a `<facsimile>` element: one `<surface>` per page, one `<zone>` (a rectangle) per bar. Each bar of the music points to its rectangle:

```xml
<facsimile>
  <surface xml:id="surface_aea1770d9c33" n="1">
    <graphic target="https://api.digitale-sammlungen.de/iiif/image/v2/bsb00023199_00013/full/4134,/0/default.jpg"
             width="4134" height="5495"/>
    <zone xml:id="zone_6ff938b3aec349c48e" type="measure" ulx="852" uly="945" lrx="1593" lry="2290"/>
    <!-- one zone for each of the other 14 bars on the page -->
  </surface>
</facsimile>
...
<pb n="1" facs="#surface_aea1770d9c33"/>
<measure n="1" facs="#zone_6ff938b3aec349c48e"> ... </measure>
```

*(Shortened from the file in Demo E below. The coordinates are pixels in the 4,134-pixel-wide version of the scan.)* The encoding stays tied to its witness: every bar can be checked against the page, the source's page and system breaks are kept, and the editor's reading sits next to what the source shows. A traditional critical edition replaces the source with a new engraving and moves the differences into a critical report.

This is where the course is going. The tools of CAMAT, which we use from the next sessions on, grew out of encoding volumes of *Denkmäler deutscher Tonkunst* from the Bayerische Staatsbibliothek's scans: optical music recognition (OMR) page by page, correction in [mei-friend](https://mei-friend.mdw.ac.at/), automatic checks, and measure zones that link every bar back to the scan.

### Demo E: a facsimile-linked page

The first page of Dietrich Buxtehude's Sonata I in F major, Op. I, for violin, viola da gamba and harpsichord, as printed in *Denkmäler deutscher Tonkunst*, vol. 11 (1903). Left: the Bayerische Staatsbibliothek's scan, with the zones from the MEI file drawn on it. Right: the same MEI file rendered by Verovio, with the page's three systems. Point at a bar on either side to find it on the other; click to compare it close up.

<div data-demo="facsimile" data-mei="facsimile/buxtehude_op1_01_page1.mei"
     data-title="Denkmäler deutscher Tonkunst 11 (1903), page 3: Buxtehude, Sonata I, bars 1 to 15"></div>

Look at bar 11. The 1903 print has the violin's C♯ as a sixteenth note; the encoding follows the first edition, printed in Buxtehude's lifetime, and makes it an eighth note, and an `<annot>` in the MEI file says so. The scan stays the witness, and the encoding records where and why it departs from it. (The note calls the first edition "the 1696 print"; sources date Op. I to about 1694 and Op. II to 1696, so treat the year with care.) The full workflow (OMR, correction, checks) comes later in the course.

!!! info "Source and licence"
    MEI: the first page (bars 1–15) of `buxtehude_op1_01_sonata_f_major_corr.mei` from the CAMAT corpus edition [*DdT 1, vol. 11: Dietrich Buxtehude, Instrumental Works*](https://github.com/egorpol/DdT_1_vol_11) (work in progress, commit `7af4ae8`), [MIT License](examples/facsimile/LICENSE); two ties into bar 16 on the next page were removed. [Download the MEI file](examples/facsimile/buxtehude_op1_01_page1.mei){: download="buxtehude_op1_01_page1.mei" }. Scan: Bayerische Staatsbibliothek, [`bsb00023199`, image 13](https://www.digitale-sammlungen.de/en/view/bsb00023199?page=13) (copy of the Hochschule für Musik und Theater München, Bibliothek), licensed [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The page loads the scan from the library's IIIF server when you open it; it is not copied here.

*Discussion: Is a facsimile-linked encoding more authentic than a clean modern edition? Authentic to what: the source, the work, the performance?*

## 4. Notation for human readers: systems made for users

Click a source to see the notation itself. The manuscripts from St. Gallen and Munich open in the library's own viewer, where you can zoom in and turn the pages; the other pictures are on Wikimedia Commons.

| System | Records | Computational analogy | Look at a source |
|---|---|---|---|
| Greek alphabetic notation ([Seikilos epitaph](https://en.wikipedia.org/wiki/Seikilos_epitaph)) | symbols mapped to pitches | lookup table | [the stele](https://commons.wikimedia.org/wiki/File:Seikilos_epitaph_04.jpg), 1st or 2nd century, National Museum of Denmark: the pitch signs are written above the text |
| [Neumes](https://en.wikipedia.org/wiki/Neume) (9th century onward) | melodic contour, often without fixed pitch | relative constraints | [Cantatorium of St. Gallen](https://www.e-codices.unifr.ch/en/csg/0359/23), about 922–925 (Stiftsbibliothek St. Gallen, Cod. Sang. 359, p. 23, on e-codices): neumes above the text, no staff lines |
| [Guidonian hand](https://en.wikipedia.org/wiki/Guidonian_hand), staff lines | pitch as a position in space | spatial lookup | [a hand with a small staff on each finger](https://commons.wikimedia.org/wiki/File:UCB_Music_Library_MS_1087.jpg), 16th century (UC Berkeley, Music Library MS 1087) |
| [Mensural notation](https://en.wikipedia.org/wiki/Mensural_notation) | durations that depend on context | rule engine | [Hartmann Schedel's songbook](https://www.digitale-sammlungen.de/en/view/bsb00079055?page=41), 1460s (Bayerische Staatsbibliothek, Cgm 810, f. 18r): one voice after another, no score |
| [Lute and organ tablature](https://en.wikipedia.org/wiki/Tablature) | where to put the fingers, not which pitch | instruction set for one instrument | organ: [Buxheim Organ Book](https://www.digitale-sammlungen.de/en/view/bsb00104633?page=31), about 1460–1470 (Bayerische Staatsbibliothek, Mus.ms. 3725, f. 9r): the top voice on a staff, the lower voices as letter names; vihuela (a Spanish relative of the lute): [Miguel de Fuenllana, *Orphénica lyra*](https://commons.wikimedia.org/wiki/File:Vihuela-Tab_Fuenllana_1554.jpg), Seville 1554: fret numbers on six lines, one line per course of strings |
| Jeongganbo (Korea, 15th century onward) | time as a grid of cells | temporal grid, close to a piano roll | [*Daeak hubo*](https://commons.wikimedia.org/wiki/File:Museum_of_Traditional_Korean_Music_041.JPG) (1759), a collection of court music, photographed in the Museum of Traditional Korean Music, Seoul: one cell per beat; [*Six Dragons Fly Again*](https://arxiv.org/abs/2408.01096) (ISMIR 2024) encodes jeongganbo for machine learning |

Notations were also made for particular groups of users:

| Notation | Made for | Look at an example |
|---|---|---|
| [Shape notes](https://en.wikipedia.org/wiki/Shape_note) | singing schools: the shape of the note head gives the syllable | ["Star in the East"](https://commons.wikimedia.org/wiki/File:Star_in_the_east.png) in *The Southern Harmony* (1854 edition) |
| [Jianpu](https://en.wikipedia.org/wiki/Numbered_musical_notation) | teaching and amateur music-making: scale degrees as numbers | ["Amazing Grace" in jianpu](https://commons.wikimedia.org/wiki/File:AmazingGraceNumberedMusicalNotation.png) |
| [Music Braille](https://en.wikipedia.org/wiki/Braille_music) | blind musicians, who read it with their fingers | [a summary of the signs](https://commons.wikimedia.org/wiki/File:Braillemusicsummary.gif) |
| [Klavarskribo](https://en.wikipedia.org/wiki/Klavarskribo) | keyboard players: the music runs down the page, low notes left and high notes right, and the staff lines are the black keys | [a keyboard with the staff growing out of it](https://en.wikipedia.org/wiki/File:KlavarExplain_1-E.png): a piano roll on paper |

There was never one "music notation"; notations are tools built for a use, and encoding formats continue that tradition.

Chant is still encoded today, in GABC and Volpiano; Verovio reads both (the GABC example is in [part 8](#8-todays-formats-in-verovio)).

## 5. Notation for machines: barrels, rolls, punched cards

When the reader is a machine, notation becomes a program: positions on a cylinder or holes in paper that trigger sound.

| When | What | Why it matters here |
|---|---|---|
| 9th century, Baghdad | Banū Mūsā, *Book of Ingenious Devices*: an automatic flute player driven by a rotating pinned cylinder | often called an early programmable machine (a popular claim, not a consensus) |
| 17th century onward | pinned barrels in barrel organs and music boxes | music stored as physical positions |
| 1801–1804 | Jacquard loom: punched cards control weaving patterns | not music, but punched cards become the medium of music machines and computers |
| 1843 | Ada Lovelace's notes on the Analytical Engine | if the relations of pitched sounds could be expressed in symbols, the engine might compose music: the encoding problem, stated before computers existed |
| 1890s | Edwin Votey's piano player, sold by Aeolian as the Pianola (1897) | executable notation for the mass market |
| 1904 | Welte-Mignon reproducing piano (Edwin Welte and Karl Bockisch, Freiburg; public launch 1905) | records tempo, dynamics and pedalling, not only notes |
| 1908 | US manufacturers agree on an 88-note roll standard in Buffalo (most sources say December 1908; some give 1910 or 1911) | a format standard: any roll plays on any instrument |
| from 1948 | Conlon Nancarrow punches his *Studies for Player Piano* by hand | the roll as a medium for music no human can play |

### Demo A: Debussy plays *Children's Corner*

Debussy recorded *Children's Corner* himself for the Welte-Mignon (roll 2733). Stanford's [SUPRA archive](https://supra.stanford.edu) scanned the roll; you can see it in [Stanford's viewer](https://purl.stanford.edu/dc920rk8870). SUPRA turned the scan into two MIDI files:

- **raw:** every hole becomes an event: 33,508 holes in 4 tracks (bass and treble notes, and two tracks of expression holes that control loudness);
- **expressive:** holes merged into notes and the expression holes turned into loudness and pedalling: 6,031 notes.

<div data-demo="roll"
     data-exp="https://raw.githubusercontent.com/pianoroll/SUPRA/master/welte-red/midi-exp/dc920rk8870_exp.mid"
     data-raw="https://raw.githubusercontent.com/pianoroll/SUPRA/master/welte-red/midi-raw/dc920rk8870_raw.mid"></div>

Compare the two versions over the same seconds. A long note on the roll is punched as a chain of holes: at 5.1 s the C3 is a 0.1-second hole in the raw file but a 3-second note in the expressive file.

*Is a roll a score, a recording or a program? Where are the bar lines and the quarter notes? What is a "note" when 33,508 holes become 6,031 notes?*

!!! info "Source and licence"
    MIDI files: SUPRA, Stanford University Piano Roll Archive, roll `dc920rk8870`, licensed [CC BY-NC-SA 4.0](https://github.com/pianoroll/SUPRA). Cite: Zhengshan Shi, Craig Stuart Sapp, Kumaran Arul, Jerry McBride and Julius O. Smith III, "SUPRA: Digitizing the Stanford University Piano Roll Archive", *ISMIR 2019*. The page fetches the files from GitHub when you click the button. Notes are played by a plain synthesiser in your browser, not a piano.

## 6. Setup: Jupyter4NFDI

The second half of block 1 is for getting everyone into Jupyter4NFDI: see [Setup on Jupyter4NFDI](../../setup.md). If it does not work for you today, follow block 2 on this page, which needs no login.

## 7. Notation for computers, 1940s to the 1990s

| When | System | People | Made for |
|---|---|---|---|
| 1940s | punched cards for *Barbara Allen* tune variants | Bertrand Bronson | sorting folk tunes into families |
| 1950–1951 | CSIRAC (Australia) plays tunes; the BBC records the Ferranti Mark 1 in 1951 | Christopher Strachey (Ferranti) | computers *play* music (no CSIRAC recording survives; it was reconstructed) |
| 1957 | *Illiac Suite* for string quartet | Lejaren Hiller, Leonard Isaacson | computers *compose* (the output was copied into a score by hand) |
| 1960s | DARMS (Ford-Columbia Music Representation) | Stefan Bauer-Mengelberg | computer-printed parts for the New York Philharmonic, typed by counting lines and spaces |
| 1964 | Plaine & Easie Code | Barry S. Brook, Murray Gould | incipits typed on an ordinary typewriter; RISM adopted it for incipits and still uses it |
| from 1982 | EsAC and the Essen Folksong Collection | Helmut Schaffrath | folksongs on DOS PCs; pitches as scale degrees, inspired by jianpu |
| 1983 | MIDI | instrument makers | performance events between instruments, not notation: the piano roll's descendant |
| 1984 | CCARH and MuseData | Walter Hewlett | large encoded repertories |
| 1980s–1990s | Humdrum toolkit and `**kern` | David Huron | analysis with Unix text tools, one column ("spine") per voice; *kern* is German for "core" |
| 1980s–1990s | ABC | Chris Walshaw | folk tunes typed as letters; the text format behind music language models such as ChatMusician (2024) |

The 1960s needed music for **printing** (DARMS) and **cataloguing** (Plaine & Easie). The 1980s brought **corpora for analysis** (Essen, MuseData, kern). Folk song made the first large data sets because single melodic lines were simple enough to encode at scale. After 1999 came MEI (Perry Roland's XML schema, built on the principles of TEI) for editions, and from 2000 MusicXML (Recordare) for exchange between notation programs.

??? note "Dates that are given differently in different sources"
    - **DARMS:** conceived 1961 (Wikipedia) or 1966 (CCARH wiki); funding is given as 1964–1976. Hence "1960s".
    - **Humdrum:** "1980s" in some sources, "1990s" in others; the toolkit was reviewed in *Music Theory Online* in 1996.
    - **Illiac Suite:** usually 1957; one source names a 1956 premiere.
    - **Bronson:** the punched-card study is dated "1940s" in the source found; the original article is not confirmed.
    - **Lovelace:** the wording of the quotation varies between transcriptions.

## 8. Today's formats in Verovio

Verovio reads all six text encodings from part 1 and renders them as notation. Edit any box: the score follows as you type. *Show as MEI* converts the text to MEI; *Piano roll* draws the notes as time × pitch, the view from Demo A.

<div data-demo="formats" data-examples="examples/"></div>

**Try this:**

1. Change a note in the ABC and in the kern version. Add a sharp (`^F` in ABC, `f#` in kern).
2. Change the metre to 3/4 (`M:3/4` in ABC, `*M3/4` in kern). What does Verovio do with bars that no longer fit?
3. Compare what each format records beyond the notes: the phrase brackets in EsAC, the spines in kern, `<divisions>` in MusicXML, the header and the `xml:id` of every element in MEI.
4. Break the syntax on purpose and read the message under the score. (Some broken inputs make Verovio crash rather than complain; the page catches those and says what is wrong.)

## 9. Binary notation: holes, grids and what survives

A perforation is binary: there is a hole at a position, or there is not. The raw roll in Demo A is exactly that. The same idea turns a melody into a grid with one row per pitch and one column per time step. *Which bars of* Alle meine Entchen *can you no longer tell apart?*

<div data-demo="grid" data-examples="examples/"></div>

- Bars 2 (two half notes), 3 (four quarter notes) and 4 (one whole note) all become a run of four cells. Pure occupancy loses where one note ends and the next begins.
- **Resolution is a choice.** A quarter-note grid cannot hold eighth notes; add some to the melody and watch them disappear. CAMAT's default cell is a sixteenth note. Finer grids cost size.
- **What would fix it?** A second grid that marks where notes start ("keep an onset grid"), or keeping a note table next to the grid, as CAMAT does, with identifiers that point back into the score.

## 10. An LLM writes ABC

ABC is compact text, and there are many tune collections online in it, so language models have seen a lot of it. We ask a model for a melody and check the answer. Because the answer is an encoding, we can test it, which a picture of a score would not allow.

<div data-demo="llm" data-answers="examples/llm/answers.json"></div>

*Does every bar add up to the metre? Does Verovio warn? Are the key and the range what was asked for? Is the kern valid at all?* Note that the checks rely on how Verovio reads the text: Verovio 6.3, for example, ignores a length written after a chord (`[DFA]2`), and the page warns when it sees one.

You do not need your own LLM account for this: the recorded answers and the instructor's demo are enough.

## 11. Wrap-up

- The three questions once more: *who reads it, what does it record, what does it leave out?* Apply them to a scan, to the grid and to the LLM's ABC.
- Where the course goes: digital edition (MEI, facsimiles) → CAMAT note tables and piano rolls → statistics and pattern search.

**Homework**

1. If setup did not work in class, finish it with the [setup page](../../setup.md) and run `01_formats_verovio.ipynb`.
2. Encode the first phrase of a melody of your choice in ABC or kern and render it (here in [part 8](#8-todays-formats-in-verovio) or in the notebook).
3. Write down one thing about the melody that your encoding cannot express.

## Notebooks

The notebooks repeat the demos with inputs you can change. On Jupyter4NFDI, one cell copies them into your workspace (see [setup](../../setup.md#get-the-session-notebooks)); you can also download them here and upload them. Each one starts with a cell that installs what it needs (Verovio 6.3.0, mido, matplotlib, ipywidgets).

- [`01_formats_verovio.ipynb`](notebooks/01_formats_verovio.ipynb){: download="01_formats_verovio.ipynb" }: Demos B and D, the seven encodings and the LLM's melody. Start here.
- [`01_player_piano.ipynb`](notebooks/01_player_piano.ipynb){: download="01_player_piano.ipynb" }: Demo A, Debussy's roll as raw and expressive MIDI. Downloads the MIDI files from GitHub when you run it.
- [`01_binary_grid.ipynb`](notebooks/01_binary_grid.ipynb){: download="01_binary_grid.ipynb" }: Demo C, the melody as a 0/1 grid and back.

## Sources

- Background reading on historical notation and on the systems in parts 5 and 7: [DARMS](https://en.wikipedia.org/wiki/DARMS_notation), [Plaine & Easie Code](https://en.wikipedia.org/wiki/Plaine_%26_Easie_Code), [ESAC (CCARH)](https://wiki.ccarh.org/wiki/ESAC), [Humdrum review, *Music Theory Online* 2.7 (1996)](https://mtosmt.org/issues/mto.96.2.7/mto.96.2.7.wild.html), [ABC history](https://abcnotation.com/history), [MuseData](https://wiki.ccarh.org/wiki/MuseData), [MEI](https://music-encoding.org/about), [MusicXML: the first decade](https://michaelgood.info/publications/music/musicxml-the-first-decade/).
- Machines and early computers: [Piano roll](https://en.wikipedia.org/wiki/Piano_roll), [Welte-Mignon](https://en.wikipedia.org/wiki/Welte-Mignon), [CSIRAC music](https://cis.unimelb.edu.au/about/csirac/music), [Ferranti Mark 1](https://en.wikipedia.org/wiki/Ferranti_Mark_1), [Illiac Suite](https://en.wikipedia.org/wiki/Illiac_Suite), [Banū Mūsā reconstruction (ZKM)](https://zkm.de/en/node/62659), [Ada Lovelace (Computer History Museum)](https://www.computerhistory.org/babbage/adalovelace/).
- SUPRA: [supra.stanford.edu](https://supra.stanford.edu), [GitHub pianoroll/SUPRA](https://github.com/pianoroll/SUPRA).
- Scores and rights: [eu-pd-composers](https://github.com/egorpol/eu-pd-composers), [IIIF](https://iiif.io), [MEI facsimiles (MEI guidelines)](https://music-encoding.org/guidelines/v5/content/facsimilesrecordings.html), [CAMAT corpus edition DdT 1, vol. 11](https://github.com/egorpol/DdT_1_vol_11), [BSB digital collections](https://www.digitale-sammlungen.de).
- ChatMusician: [arXiv 2402.16153](https://arxiv.org/abs/2402.16153).
- Rendering: [Verovio](https://www.verovio.org) 6.3.0.
