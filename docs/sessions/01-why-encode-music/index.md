# 1. Why encode music? From notation to machine-readable scores

Session 1, 15 October 2026 (double session, 2 × 90 minutes).

Every notation is already an encoding. It was made for a particular reader and a particular use, and it writes down some things while leaving others to the reader's knowledge. Computers, and now language models, are readers without that knowledge, so music encoding formats must state explicitly what human readers infer. Formats differ for the same reason historical notations differ: they serve different users and tasks.

!!! tip "How to use this page"
    The demos on this page run in your browser; nothing needs to be installed. They load [Verovio](https://www.verovio.org) (about 12 MB) the first time you use them. The same demos come as Jupyter notebooks, where you can change the inputs and keep your work: see [Notebooks](#notebooks) at the end.

??? info "What is Verovio?"
    Verovio is the program that turns an encoding into a score you can see on this page. It *engraves* music: it reads an encoded score and draws it as notation (an SVG image). It is built around MEI and converts the other formats on the fly: kern, MusicXML, ABC, Plaine & Easie, EsAC, and the chant formats GABC and Volpiano. It is free and open source (LGPL licence), and the [RISM Digital Center](https://rism.digital) leads its development.

    Verovio is written in C++ and comes in versions for other languages. This page uses the JavaScript version, which runs inside your browser; the notebooks use the Python version (`pip install verovio`). Both are version 6.3.0, so page and notebooks show the same score. You can also try it in the [Verovio editor](https://editor.verovio.org), and CAMAT, the library we use from session 2, renders scores with it.

    Verovio only shows what the encoding says. When a score looks wrong, look at the encoding first, and then at how Verovio reads it: parts 8 and 10 do both.

**By the end of the session you can**

1. explain why a score made for human readers is not enough for a computer;
2. ask three questions of any notation or format: *Who reads it? What does it record? What does it leave out?*;
3. tell a scan, a PDF, an encoded score and a facsimile-linked edition apart, and say who can use each;
4. place key systems on a timeline from mechanical instruments to kern and the Essen folksong collection;
5. edit a short ABC, kern or MEI text and render it with Verovio;
6. turn a melody into a 0/1 grid and say what the grid loses;
7. check an LLM-written melody against what was asked for.

## 1. One melody, seven encodings

Here are the first four bars of *Alle meine Entchen*, seven times. Before anything is rendered: *Which of these is the music? Which can you read? Which can a computer read?* The last tab shows the same bars as a score, for reference.

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

=== "Common notation"

    For reference: the four bars in common staff notation, drawn by Verovio from the MEI tab.

    *Loading the score…*
    {: data-demo="score" data-file="examples/alle_meine_entchen.mei" data-format="mei" }

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

The first page of Dietrich Buxtehude's Sonata I in F major, Op. I, for violin, viola da gamba and harpsichord, as printed in *Denkmäler deutscher Tonkunst*, vol. 11 (1903). Left: the Bayerische Staatsbibliothek's scan, with the zones from the MEI file drawn on it. Right: the same MEI file rendered by Verovio, with the page's three systems. Point at a bar on either side to find it on the other; click to compare it close up. Tick *Show the bar's MEI* to read how the selected bar is encoded.

<div data-demo="facsimile" data-mei="facsimile/buxtehude_op1_01_page1.mei"
     data-title="Denkmäler deutscher Tonkunst 11 (1903), page 3: Buxtehude, Sonata I, bars 1 to 15"></div>

Look at bar 11. The 1903 print has the violin's C♯ as a sixteenth note; the encoding follows the first edition, printed in Buxtehude's lifetime, and makes it an eighth note, and an `<annot>` in the MEI file says so. With *Show the bar's MEI* ticked you can read it in the code: `<staff n="1">` is the violin, `n="2"` the viola da gamba and `n="3"` the harpsichord's bass line; each `<harm>` holds a figure of the figured bass; and the `<annot>` points at the C♯ with `plist`. The scan stays the witness, and the encoding records where and why it departs from it. (The note calls the first edition "the 1696 print"; sources date Op. I to about 1694 and Op. II to 1696, so treat the year with care.) The full workflow (OMR, correction, checks) comes later in the course.

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

Click a source to see the machine or its notation: book scans on the Internet Archive, photographs on Wikimedia Commons, and a museum's reconstruction.

| When | What | Why it matters here | Look at a source |
|---|---|---|---|
| 9th century, Baghdad | Banū Mūsā, *The Instrument That Plays by Itself*: an automatic flute player driven by a rotating pinned cylinder | often called an early programmable machine (a popular claim, not a consensus) | [a reconstruction](https://zkm.de/en/artwork/automatische-hydraulische-orgel-der-banu-musa-ibn-shakir) built from the treatise at ZKM Karlsruhe (2015) |
| 17th century onward | pinned barrels in barrel organs and music boxes | music stored as physical positions | [Salomon de Caus's water-driven barrel organ](https://commons.wikimedia.org/wiki/File:Barrel-organ_1.png) (1615), as redrawn in the 1911 *Encyclopædia Britannica*; Joseph Engramelle, [*La tonotechnie, ou l'art de noter les cylindres*](https://archive.org/details/latonotechnieoul0000engr/page/n290/mode/1up) ("the art of notating cylinders"), Paris 1775, plate III: a march written out for a barrel, with the barrel's divisions numbered under the notes |
| 1801–1804 | Jacquard loom: punched cards control weaving patterns | not music, but punched cards become the medium of music machines and computers | [a Jacquard loom with its chain of punched cards](https://commons.wikimedia.org/wiki/File:A_Jacquard_loom_showing_information_punchcards,_National_Museum_of_Scotland.jpg), National Museum of Scotland: each card controls one row of the weave |
| 1843 | Ada Lovelace's notes on the Analytical Engine | if the relations of pitched sounds could be expressed in symbols, the engine might compose music: the encoding problem, stated before computers existed | [her Note A, p. 694](https://archive.org/details/india.history.resource.53369/page/694/mode/1up), in *Scientific Memoirs*, vol. 3 (London, 1843): the sentence on music is in the upper half of the page |
| 1890s | Edwin Votey's piano player, sold by Aeolian as the Pianola (1897) | executable notation for the mass market | [a roll in a Pianola](https://commons.wikimedia.org/wiki/File:Pianola_Museum_4.JPG) (Pianola Museum, Amsterdam): the player steers the pointer along the wavy Metrostyle line, which sets the tempo; [the first Pianola](https://commons.wikimedia.org/wiki/File:First_Pianola_%28cropped%29.jpg), photographed in 1922 when it was given to the Smithsonian |
| 1904 | Welte-Mignon reproducing piano (Edwin Welte and Karl Bockisch, Freiburg; public launch 1905) | records tempo, dynamics and pedalling, not only notes | Debussy's roll from [Demo A](#demo-a-debussy-plays-childrens-corner) in [Stanford's viewer](https://purl.stanford.edu/dc920rk8870): zoom in to see the holes |
| 1908 | US manufacturers agree on an 88-note roll standard in Buffalo (most sources say December 1908; some give 1910 or 1911) | a format standard: any roll plays on any instrument | [the box of an 88-note roll](https://commons.wikimedia.org/wiki/File:88_NOTE,_THEMODIST-METROSTYLE,_92882,_Follies_of_1910._%28piano_roll%29_-_The_Aeolian_Company,_New_York._The_Orchestrelie_Company,_London._Made_in_U.S.A..jpg) (Aeolian, *Follies of 1910*): "88 NOTE" on the label tells the buyer which players it fits |
| from 1948 | Conlon Nancarrow punches his *Studies for Player Piano* by hand | the roll as a medium for music no human can play | [Nancarrow at his punching machine](https://www.paul-sacher-stiftung.ch/en/research/1-2-Conlon-Nancarrow-Edition-project.html) and a page of his score of Study No. 37 (Paul Sacher Stiftung, Basel, which holds his rolls and manuscripts) |

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

Click a source to see or hear it. The encoded scores open in the Verovio Humdrum Viewer, which is built on Verovio and shows the code next to the notation.

| When | System | People | Made for | Look at a source |
|---|---|---|---|---|
| 1940s | punched cards for *Barbara Allen* tune variants | Bertrand Bronson | sorting folk tunes into families | the cards are not online; [*Barbara Allen* as sung in a California migrant camp in 1940](https://blogs.loc.gov/folklife/2017/02/song-of-the-week-barbara-allen/) (Library of Congress blog, two recordings) is one of the variants |
| 1950–1951 | CSIRAC (Australia) plays tunes; the BBC records the Ferranti Mark 1 in 1951 | Christopher Strachey (Ferranti) | computers *play* music (no CSIRAC recording survives; it was reconstructed) | [the music of CSIRAC](https://cis.unimelb.edu.au/about/history/csirac/music) (University of Melbourne): the reconstructed *Colonel Bogey* and the 1951 Ferranti recording; [how the Ferranti recording was restored](https://www.bl.uk/stories/blogs/posts/restoring-the-first-recording-of-computer-music) (British Library) |
| 1957 | *Illiac Suite* for string quartet | Lejaren Hiller, Leonard Isaacson | computers *compose* (the output was copied into a score by hand) | [the first page of the score](https://archive.org/details/experimentalmusi00hill/page/182/mode/1up), printed in their book *Experimental Music* (1959) |
| 1960s | DARMS (Ford-Columbia Music Representation) | Stefan Bauer-Mengelberg | computer-printed parts for the New York Philharmonic, typed by counting lines and spaces | [how DARMS numbers the lines and spaces](https://commons.wikimedia.org/wiki/File:How_the_Space_Code_is_assigned_within_the_DARMS_music_encoding_language.png) (a diagram drawn for Wikipedia): the bottom line of the staff is 21 |
| 1964 | Plaine & Easie Code | Barry S. Brook, Murray Gould | incipits typed on an ordinary typewriter; RISM adopted it for incipits and still uses it | [a RISM record](https://rism.online/sources/190006990) of a Buxtehude sonata copied in the 1690s (Uppsala University Library): the incipit of each movement is stored as Plaine & Easie and drawn as notation |
| from 1982 | EsAC and the Essen Folksong Collection | Helmut Schaffrath | folksongs on DOS PCs; pitches as scale degrees, inspired by jianpu | [*Schlaf, Kindlein, schlaf*](https://verovio.humdrum.org/?file=https://raw.githubusercontent.com/ccarh/essen-folksong-collection/main/europa/deutschl/kinder/kindr001.krn), song K0001 of the collection in its kern version: the curly brackets mark the phrases of the EsAC original (EsAC itself is in [part 8](#8-todays-formats-in-verovio)) |
| 1983 | MIDI | instrument makers | performance events between instruments, not notation: the piano roll's descendant | the two MIDI files of the Debussy roll in [Demo A](#demo-a-debussy-plays-childrens-corner); how MIDI works: [addendum](#addendum-midi-on-a-cable-and-in-a-file) |
| 1984 | CCARH and MuseData | Walter Hewlett | large encoded repertories | [Corelli, Op. 1 No. 1, first movement](https://verovio.humdrum.org/?file=github:musedata/corelli/op1/musedata/corelli-op1n01-01.msd) in MuseData |
| 1980s–1990s | Humdrum toolkit and `**kern` | David Huron | analysis with Unix text tools, one column ("spine") per voice; *kern* is German for "core" | [Bach's chorale *Aus meines Herzens Grunde* (BWV 269)](https://verovio.humdrum.org/?file=https://raw.githubusercontent.com/craigsapp/bach-370-chorales/main/kern/chor001.krn), one spine per voice |
| 1980s–1990s | ABC | Chris Walshaw | folk tunes typed as letters; the text format behind music language models such as ChatMusician (2024) | [*The Kesh*](https://thesession.org/tunes/55), an Irish jig on The Session: dozens of settings, each in ABC and as notation |

The 1960s needed music for **printing** (DARMS) and **cataloguing** (Plaine & Easie). The 1980s brought **corpora for analysis** (Essen, MuseData, kern). Folk song made the first large data sets because single melodic lines were simple enough to encode at scale. After 1999 came MEI (Perry Roland's XML schema, built on the principles of TEI) for editions, and from 2000 MusicXML (Recordare) for exchange between notation programs.

??? note "Dates that are given differently in different sources"
    - **DARMS:** conceived 1961 (Wikipedia) or 1966 (CCARH wiki); funding is given as 1964–1976. Hence "1960s".
    - **Humdrum:** "1980s" in some sources, "1990s" in others; the toolkit was reviewed in *Music Theory Online* in 1996.
    - **Illiac Suite:** usually 1957; one source names a 1956 premiere.
    - **Bronson:** the punched-card study is dated "1940s" in the source found; the original article is not confirmed.
    - **Lovelace:** the wording of the quotation varies between transcriptions.

## 8. Today's formats in Verovio

Verovio reads all six text encodings from part 1 and renders them as notation. Edit any box: the score follows as you type. *Show as MEI* converts the text to MEI; *Piano roll* draws the notes as time × pitch, the view from Demo A.

Where each format comes from, and where to find real files in it (the history is in [part 7](#7-notation-for-computers-1940s-to-the-1990s)):

| Format | Made by, when | Made for | Documentation | Real files |
|---|---|---|---|---|
| ABC | Chris Walshaw, 1980s–1990s | folk and traditional tunes, typed and shared as plain text | [ABC standard 2.1](https://abcnotation.com/wiki/abc:standard:v2.1) | [The Session](https://thesession.org/tunes): folk tunes, each setting in ABC and as notation |
| Humdrum `**kern` | David Huron, 1980s–1990s | analysis with text tools: one column ("spine") per voice | [the `**kern` reference](https://www.humdrum.org/rep/kern/) | [Bach's 370 chorales](https://github.com/craigsapp/bach-370-chorales) on GitHub; open any kern file in the [Verovio Humdrum Viewer](https://verovio.humdrum.org/) |
| Plaine & Easie | Barry S. Brook and Murray Gould, 1964 | incipits in library catalogues; RISM still uses it | [the code](https://www.iaml.info/plaine-easie-code), maintained by IAML | [RISM Online](https://rism.online/) stores its incipits in it, for example in [this Buxtehude sonata](https://rism.online/sources/190006990) |
| EsAC | Helmut Schaffrath, Essen, from 1982 | folk-song collections: one record per song, with region (`REG`), key and metre (`KEY`) and the melody as scale degrees (`MEL`) | [how the Verovio Humdrum Viewer reads EsAC](https://doc.verovio.humdrum.org/interface/esac/), with [a record from the Essen collection](https://doc.verovio.humdrum.org/interface/esac/b0029.txt) | the [Essen Folksong Collection](https://github.com/ccarh/essen-folksong-collection), over 6,000 songs, converted to kern |
| MusicXML | Michael Good (Recordare), from 2000; now the W3C Music Notation Community Group | exchange between notation programs | [MusicXML 4.0](https://www.w3.org/2021/06/musicxml40/) (2021), with a tutorial | [a list of sites with MusicXML files](https://www.musicxml.com/music-in-musicxml/); notation programs such as MuseScore export it |
| MEI | Perry Roland, from 1999; now the MEI community | scholarly editions | [the MEI Guidelines](https://music-encoding.org/guidelines/v5/content/) (version 5) | [MEI sample encodings](https://github.com/music-encoding/sample-encodings) on GitHub; the Buxtehude page in [Demo E](#demo-e-a-facsimile-linked-page) |
| GABC (chant) | a monk of the Abbey of Sainte-Madeleine du Barroux, improved by Élie Roux and others | typesetting Gregorian chant with the Gregorio software | [GABC, described by the Gregorio project](https://gregorio-project.github.io/gabc/) | [GregoBase](https://gregobase.selapa.net/), a database of chants, each one downloadable as GABC |

MIDI is not on this list: it records what a player does, not what a score shows. See the [addendum](#addendum-midi-on-a-cable-and-in-a-file).

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
- **Two grids are one grid with three values.** With the onset grid ticked, each cell is in one of three states: 0 = silence, 1 = a note continues, 2 = a note starts. Two yes/no grids would allow four combinations, but "a note starts where nothing sounds" cannot happen, so three are left: the notation is no longer binary but *ternary*. Every cell that is not 0 still says "sounding", so a tool written for the 0/1 grid can read the new grid too.

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

## Addendum: MIDI on a cable and in a file

MIDI comes up in Demo A and in part 7. The name is used for two things: messages sent between instruments, and files that store them.

**On a cable: messages, sent as they happen.** MIDI 1.0 was published in August 1983 so that instruments from different makers could control each other. A message says what a player does, not what it sounds like: *channel 1, key 60 down, velocity 90* is three bytes, `90 3C 5A`, and a second message follows when the key is released. The receiving instrument makes the sound; MIDI itself carries no audio. The original cable has five-pin DIN plugs, carries messages in one direction only (from an OUT to an IN socket) at 31,250 bits per second, and has 16 channels, so one cable can play 16 instruments or sounds. A message carries no time: the note starts when the message arrives, and each three-byte message takes about a millisecond on that cable. Today the same messages also travel over USB, Bluetooth and networks, or between programs on one computer.

**In a file: the same messages, each with a wait before it.** A Standard MIDI File (`.mid`) stores the messages and writes before each one how long to wait after the previous one, counted in *ticks*. The header says how many ticks make a quarter note, and a tempo message says how long a quarter note lasts. Verovio writes the four bars of *Alle meine Entchen* as a file of 144 bytes:

```text
4D 54 68 64  00 00 00 06     "MThd": the header, 6 bytes follow
00 01  00 02  00 78          format 1, 2 tracks, 120 ticks per quarter
4D 54 72 6B  00 00 00 0B     "MTrk": track 1, 11 bytes follow
  00  FF 51 03 07 A1 20        wait 0, tempo
  00  FF 2F 00                 wait 0, end of track
4D 54 72 6B  00 00 00 67     "MTrk": track 2, 103 bytes follow
  00  FF 58 04 04 02 18 08     wait 0, time signature 4/4
  00  90 3C 5A                 wait 0, key 60 (C4) down, velocity 90
  77  90 3C 00                 wait 119, key 60 at velocity 0: up
  01  90 3E 5A                 wait 1, key 62 (D4) down, velocity 90
  ...
```

The numbers are hexadecimal: `77` is 119, `3C` is 60, and the tempo `07 A1 20` is 500,000 microseconds per quarter note, 120 quarter notes a minute. In `90`, the `9` means "key down" and the `0` channel 1. Each note sounds for 119 of its quarter note's 120 ticks, and the next starts one tick later. The `90` messages are exactly what a cable carries; the `FF` messages (tempo, time signature, end of track) exist only in files. A key "down" at velocity 0 counts as released: the MIDI 1.0 specification allows both this and a separate Note Off message.

| | On a cable (or USB, Bluetooth) | In a file (`.mid`) |
|---|---|---|
| What it is | a live stream of messages | the same messages, stored |
| Time | the moment a message arrives | a wait in ticks before each message, and a tempo |
| Parts | up to 16 channels per cable | channels, and tracks played together (format 1) |
| Example | a keyboard playing a synthesiser | the two files of the Debussy roll in Demo A |

**The three questions, asked of MIDI.**

- *Who reads it?* Instruments, sequencers and recording software; SUPRA turned the Debussy roll into MIDI files.
- *What does it record?* Which key, how hard (velocity, 0 to 127), when, on which channel, and controllers such as the pedals: the pedal bands in Demo A are Control Change messages 64 (sustain pedal) and 67 (soft pedal).
- *What does it leave out?* What a score adds for a reader. C♯ and D♭ are the same key, 61. A note lasts so many ticks; it has no note value, so a short quarter note and an eighth note followed by a rest can look the same. There are no stems, beams, voices, ties, slurs or staff layout. Turning a score into MIDI is easy (Verovio does it), but turning MIDI into a score means guessing, as with the grid in part 9.

## Notebooks

The notebooks repeat the demos with inputs you can change. On Jupyter4NFDI, one cell copies them into your workspace (see [setup](../../setup.md#get-the-session-notebooks)); you can also download them here and upload them. Each one starts with a cell that installs what it needs (Verovio 6.3.0, mido, matplotlib, ipywidgets, and Bokeh for interactive piano rolls).

- [`01_formats_verovio.ipynb`](notebooks/01_formats_verovio.ipynb){: download="01_formats_verovio.ipynb" }: Demos B and D, the seven encodings and the LLM's melody. Start here.
- [`01_player_piano.ipynb`](notebooks/01_player_piano.ipynb){: download="01_player_piano.ipynb" }: Demo A, Debussy's roll as raw and expressive MIDI. Downloads the MIDI files from GitHub when you run it.
- [`01_binary_grid.ipynb`](notebooks/01_binary_grid.ipynb){: download="01_binary_grid.ipynb" }: Demo C, the melody as a 0/1 grid and back.

## Sources

- Background reading on historical notation and on the systems in parts 5 and 7: [DARMS](https://en.wikipedia.org/wiki/DARMS_notation), [Plaine & Easie Code](https://en.wikipedia.org/wiki/Plaine_%26_Easie_Code), [ESAC (CCARH)](https://wiki.ccarh.org/wiki/ESAC), [Humdrum review, *Music Theory Online* 2.7 (1996)](https://mtosmt.org/issues/mto.96.2.7/mto.96.2.7.wild.html), [ABC history](https://abcnotation.com/history), [MuseData](https://wiki.ccarh.org/wiki/MuseData), [MEI](https://music-encoding.org/about), [MusicXML: the first decade](https://michaelgood.info/publications/music/musicxml-the-first-decade/).
- Machines and early computers: [Piano roll](https://en.wikipedia.org/wiki/Piano_roll), [Welte-Mignon](https://en.wikipedia.org/wiki/Welte-Mignon), [CSIRAC music](https://cis.unimelb.edu.au/about/csirac/music), [Ferranti Mark 1](https://en.wikipedia.org/wiki/Ferranti_Mark_1), [Illiac Suite](https://en.wikipedia.org/wiki/Illiac_Suite), [Banū Mūsā reconstruction (ZKM)](https://zkm.de/en/node/62659), [Ada Lovelace (Computer History Museum)](https://www.computerhistory.org/babbage/adalovelace/).
- SUPRA: [supra.stanford.edu](https://supra.stanford.edu), [GitHub pianoroll/SUPRA](https://github.com/pianoroll/SUPRA).
- Scores and rights: [eu-pd-composers](https://github.com/egorpol/eu-pd-composers), [IIIF](https://iiif.io), [MEI facsimiles (MEI guidelines)](https://music-encoding.org/guidelines/v5/content/facsimilesrecordings.html), [CAMAT corpus edition DdT 1, vol. 11](https://github.com/egorpol/DdT_1_vol_11), [BSB digital collections](https://www.digitale-sammlungen.de).
- ChatMusician: [arXiv 2402.16153](https://arxiv.org/abs/2402.16153).
- MIDI: [MIDI 1.0 (MIDI Association)](https://midi.org/midi-1-0), [summary of the MIDI 1.0 messages](https://midi.org/summary-of-midi-1-0-messages), [MIDI (Wikipedia)](https://en.wikipedia.org/wiki/MIDI).
- Rendering: [Verovio](https://www.verovio.org) 6.3.0.
