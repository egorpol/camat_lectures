# 2. Building an edition: the source and the notes

Session 2, 29 October 2026 (double session, 2 × 90 minutes).

In this session we worked with Robert Schumann's *Fröhlicher Landmann, von der Arbeit zurückkehrend* (*Album für die Jugend*, Op. 68 No. 10). An edition is more than an encoding of the notes: it names the source it follows, links every bar to a scan of that source, records what the editor changed and why, and lets others check it. Our encoding uses MEI (Music Encoding Initiative), a text format for scores. Verovio turns that text into a score on the screen. This page follows the class: setup, preparing the page image, and demonstrations of how the scan, the encoding and the drawn score work together.

!!! tip "How to use this page"
    Follow the parts in order. Parts marked *shown* were demonstrated in class. Use the notebook or page listed below to try them at home; session 3 goes through the route again, hands-on. If you only have a tablet, use the **Cloud** tab in [part 1](#1-setup). The [Notebooks](#notebooks) section has the downloads.

**By the end of the session you can**

1. open and run the seminar notebooks on your own laptop, or in the cloud;
2. tell a printed source, its scan, an encoding and an edition apart;
3. prepare the page of a source as an image and find its bars;
4. say what optical music recognition (OMR) gives you, and why you still compare it with the scan;
5. say why each note in Verovio's drawing carries the identifier (`xml:id`) of its MEI element.

You have also seen two steps you do yourself in session 3: linking each bar to the scan and editing the MEI file with Copilot, the chat assistant in VS Code.

**Today in short**

| Part | In class | Notebook or page |
|---|---|---|
| [1. Setup](#1-setup) | most of block 1 | [`02_pdf_preparation.ipynb`](notebooks/02_pdf_preparation.ipynb), up to the first check |
| [2. Source, scan, encoding, edition](#2-source-scan-encoding-edition) | to read | this page |
| [3. The page and its bars](#3-the-page-and-its-bars) | you ran it | [`02_pdf_preparation.ipynb`](notebooks/02_pdf_preparation.ipynb) |
| [4. From a scan to notes: OMR](#4-from-a-scan-to-notes-omr) | shown | [`02_schumann_omr.ipynb`](notebooks/02_schumann_omr.ipynb) |
| [5. The score as SVG](#5-the-score-as-svg) | shown | [What is SVG?](svg.md) |
| [6. Linking the bars to the scan](#6-linking-the-bars-to-the-scan) | shown | in session 3 |
| [7. Editing the MEI file live](#7-editing-the-mei-file-live) | shown | [`02_live_editing.ipynb`](notebooks/02_live_editing.ipynb) |

## 1. Setup

=== "Laptop"

    From this session on, we work on our own laptops. Follow the [setup page](../../setup-laptop.md) step by step, together in class. It installs VS Code (the editor), Miniforge (Python), the seminar's packages, and Git, and connects VS Code to your GitHub account. It ends with a check: the notebook `02_pdf_preparation.ipynb` prints `CAMAT: 0.2.8`.

    Step 4 downloads about 770 MB. While it runs, we look at [part 2](#2-source-scan-encoding-edition) together.

=== "Cloud"

    If you only have a tablet, or the laptop setup does not work today, you work in the browser: follow the [cloud route](../../setup.md#from-session-2-the-cloud-route). It starts a JupyterLab on Jupyter4NFDI with everything already installed, and ends with the same check: `02_pdf_preparation.ipynb` prints `CAMAT: 0.2.8`. Instead of VS Code you use JupyterLab.

    There is no big download, so you are ready early. Help a neighbour with the laptop setup, or read [part 2](#2-source-scan-encoding-edition) ahead.

Setup took most of block 1, and some students switched to the cloud route. If your setup is unfinished, completing it is homework. Session 3 starts with time for it.

## 2. Source, scan, encoding, edition

Four things that are easy to confuse:

- **The source.** One particular printed edition: Clara Schumann's edition of the *Album für die Jugend*, Leipzig: Breitkopf & Härtel, plate number R.S. 67 (IMSLP dates it 1887). Editors call a source like this a *witness*: it is the evidence of what the music says. Other editions of the same piece differ in details.
- **The scan.** A photograph of one copy of that print, made by the Bavarian State Library and shared on IMSLP as [file 51556](https://imslp.org/wiki/Special:ImagefromIndex/51556): a PDF of 50 pages. No. 10 fills page 8 and has five systems. The print has no bar numbers.
- **The encoding.** The notes as text a computer can read. We start from Maja Hartwig's MEI file of this piece in the [MEI Sample Collection](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei). It was made from another source, not from our print.
- **The edition.** What an editor makes from the source, the scan and the encoding: the encoding checked against the source, with every bar linked to its place on the scan, corrections and explanations in the file, and a viewer that shows all this. In session 3 you make one yourself.

## 3. The page and its bars

Continue `02_pdf_preparation.ipynb` from the check where the setup stopped. The notebook

1. downloads the scan and keeps it unchanged;
2. copies page 8 into a one-page PDF (in that file it is page 1, but its printed number stays 8);
3. draws the page as an image, which is what the links in [part 6](#6-linking-the-bars-to-the-scan) point to;
4. lists which bars are on which system and checks that against the MEI file.

The print has no bar numbers, and the MEI file numbers the pickup as bar 1. To keep one vocabulary, we count bars as musicians do: the pickup is "the pickup", and bar 1 is the first full bar. This table connects the two numberings. The notebooks print the MEI number (`n`) and each bar's identifier (`xml:id`).

| Bar | MEI `n` | System | Bar's `xml:id` |
|---|---|---|---|
| pickup | 1 | 1 | `d1e9` |
| 1 | 2 | 1 | `d1e74` |
| 2 | 3 | 1 | `d1e352` |
| 3 | 4 | 1 | `d1e648` |
| 4 | 5 | 1 | `d1e968` |
| 5 | 6 | 2 | `d1e1231` |
| 6 | 7 | 2 | `d1e1509` |
| 7 | 8 | 2 | `d1e1805` |
| 8 | 9 | 2 | `d1e2125` |
| 9–12 | 10–13 | 3 | |
| 13–16 | 14–17 | 4 | |
| 17–20 | 18–21 | 5 | |

The live editing in [part 7](#7-editing-the-mei-file-live) works on the pickup and bars 1–8, the first two systems.

## 4. From a scan to notes: OMR

An OMR program looks at the image of a page and proposes notes. It produces a draft, not a transcription: it can miss notes, misread pitches, merge bars, and it usually drops dynamics and words such as *Frisch und munter*.

This was shown in class. At home, open `02_schumann_omr.ipynb`: it shows what two OMR programs, HOMR and OeMeR, made of our page. We ran them before class (each takes minutes), so the notebook only loads the results.

Both are free, open-source research programs. You start them with a command, not in a window with buttons, and both write their result as MusicXML, a common exchange format for scores.

- **[HOMR](https://github.com/liebharc/homr)** reads photos and scans of printed music. It first finds the staff lines, note heads and bar lines in the image, then reads each staff from left to right with a *transformer*, the same kind of model that language models use. Its documentation says that it concentrates on pitch and rhythm and leaves out dynamics, articulation and other signs. We used version 0.7.0.
- **[OeMeR](https://github.com/BreezeWhite/oemer)** is the older program on which HOMR's first step is based. It sorts every pixel of the image into staff lines, note heads, stems, clefs, rests and so on, and then builds the music from these pieces, step by step. It is meant to cope with photos taken at an angle. We used version 0.1.8.

Other OMR programs work with a window: [Audiveris](https://audiveris.github.io/audiveris/), also free and open source, shows what it recognised on top of the scan, lets you correct it, and then exports MusicXML. Commercial programs work the same way.

1. Look at the scan next to HOMR's result for the first two systems.
2. Compare bar 1 and bar 5 in the bass: which pitch does HOMR read at the end of each bar?
3. Find one thing HOMR got wrong or left out.

??? info "Pitch names: C4, c′ and kleines c"
    The notebooks use scientific pitch names: middle C is **C4**, and the number goes up at each C. In German (Helmholtz) names:

    | Scientific | C3 | F3 | A3 | C4 | F4 |
    |---|---|---|---|---|---|
    | German | c (kleines c) | f | a | c′ (eingestrichenes c) | f′ |

??? note "Extension: OeMeR and running OMR yourself"
    Part 4 of the notebook shows OeMeR on the whole page: it reads most of the right hand in the bass clef, finds 19 bars instead of 21 and loses the C3 of the pickup. Part 5 runs both programs again; that needs extra installations and several minutes per page.

    Without installing anything, you can try HOMR on its [demo website](https://homr.site): upload a picture of a page (JPG or PNG; a screenshot of page 8 of the scan works) and download the MusicXML. Open it in the [Verovio editor](https://editor.verovio.org) to see what HOMR read. The website does not say who runs it, so upload only pages you may share, such as our public-domain scan.

## 5. The score as SVG

SVG (Scalable Vector Graphics) is a picture described as text; Verovio draws every score on this site as SVG. In class we went through [What is SVG?](svg.md) with its three demos. Try them at home, then use the three questions at the end as a self-check.

Every note, rest and bar in the MEI file has an identifier, its `xml:id`, such as `d1e60`. Verovio's drawing keeps that identifier on each note's group of shapes. A click on the drawing can therefore find the note in the file. Links, corrections and a language model can name exactly that note. The pitch and the length, however, are only in the MEI file: the drawing only knows where to put its shapes.

## 6. Linking the bars to the scan

An edition links each bar of the encoding to the place on the page image where it is printed. Click a bar in the score and its box lights up on the page, and the other way round.

The MEI file keeps these links in a `<facsimile>` section. It names the page image and keeps one `<zone>` per bar: a box given by its corners. Each `<measure>` (a bar) points to its zone with the attribute `facs`. An attribute is a named property in the text, such as `facs="#zone1"`.

In class we saw examples in mei-friend, an MEI editor in the browser, with the scan beside the score, and a notebook that made these links for our page. In session 3 you make the links yourself, step by step. For a finished edition with such links, see [Webern, Variations Op. 27](https://egorpol.github.io/webern_op27/).

## 7. Editing the MEI file live

At the end of class we opened `work.mei`, a copy of our starting file, in VS Code next to its score in `02_live_editing.ipynb`. Copilot added a slur from the print. The notebook drew the score again each time the file was saved and listed the changes in words.

Session 3 starts with this notebook: you add the tempo words *Frisch und munter* and the *f* by hand, and a slur with Copilot. To try it at home, open [`02_live_editing.ipynb`](notebooks/02_live_editing.ipynb) and follow its steps.

??? info "Why does the starting file have no slurs or dynamics?"
    We removed the slurs, dynamics, tempo words and articulation from Maja Hartwig's file on purpose. Restoring some of them from the print is one of the editing tasks in session 3. The file's header says exactly what was removed.

## 8. Wrap-up

- Source, scan, encoding and edition are four different things. The source is the evidence; everything else is checked against it.
- OMR and existing encodings save typing. Neither saves the comparison with the source.
- Each note in Verovio's drawing keeps the `xml:id` of its MEI element, so we can find the same note in the drawing and the file.
- Session 3 starts with time for setup and `02_live_editing.ipynb`. Then you go through the whole route again, hands-on and step by step, with the PDF of a different piece with several pages: make page images, draw a box around each bar, add the links in the MEI file, and combine the pages into one file. You also work on the MEI header: the part that describes the music and its sources, and why we need it. In session 4, we put the edition on GitHub and publish it.

**Homework**

1. If the setup did not finish in class, complete it with the [setup page](../../setup-laptop.md) until the check prints `CAMAT: 0.2.8`. If your laptop setup is stuck, use the [cloud route](../../setup.md#from-session-2-the-cloud-route) for now. If you get stuck, write down the step and the error message and bring them to session 3.
2. Compare the bass of bars 2–4 in the print with what HOMR read (`02_schumann_omr.ipynb`). Note one difference, if you find one.

## Notebooks

=== "Laptop"

    The last step of the setup copies the notebooks into `seminar-work/camat_lectures/02-building-an-edition/`.

=== "Cloud"

    Step 3 of the cloud route copies the notebooks into `work/camat_lectures/02-building-an-edition/`. Run them there: the folders they create next to them are then kept too.

Three of them need a ZIP file with data next to them; the download script copies those too.

- [`02_pdf_preparation.ipynb`](notebooks/02_pdf_preparation.ipynb){: download="02_pdf_preparation.ipynb" } with [`schumann-edition-inputs.zip`](notebooks/schumann-edition-inputs.zip): parts 1 and 3. Downloads the scan from IMSLP when you run it. The live-editing notebook uses the folder `schumann_edition_work` that it creates.
- [`02_schumann_omr.ipynb`](notebooks/02_schumann_omr.ipynb){: download="02_schumann_omr.ipynb" } with [`schumann-omr-recordings.zip`](notebooks/schumann-omr-recordings.zip): part 4.
- [`02_live_editing.ipynb`](notebooks/02_live_editing.ipynb){: download="02_live_editing.ipynb" } with [`schumann-edition-inputs.zip`](notebooks/schumann-edition-inputs.zip): part 7; session 3 starts with it.
- Optional: [`02_note_entry.ipynb`](notebooks/02_note_entry.ipynb){: download="02_note_entry.ipynb" }, skipped in class: you type bar 1 of our piece in ABC, then see the same notes in the other text formats from session 1. No ZIP needed.

## Sources

- The print: Robert Schumann, *Album für die Jugend*, Op. 68, ed. Clara Schumann, Leipzig: Breitkopf & Härtel, plate R.S. 67 ([IMSLP work page](https://imslp.org/wiki/Album_f%C3%BCr_die_Jugend,_Op.68_(Schumann,_Robert)), [file 51556](https://imslp.org/wiki/Special:ImagefromIndex/51556); scan: Bayerische Staatsbibliothek). The notebooks download it when you run them; it is not part of the course files.
- The encoding: Maja Hartwig, [*Fröhlicher Landmann*, MEI 5.1](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei), MEI Sample Collection. The file declares itself public domain; the collection is under the [ECL-2.0 licence](https://github.com/music-encoding/sample-encodings/blob/main/LICENSE). Our starting file keeps its credits.
- The full record of source and encoding: [`sources.json`](sources/sources.json).
- OMR programs: [HOMR](https://github.com/liebharc/homr), [OeMeR](https://github.com/BreezeWhite/oemer).
- A finished facsimile-linked edition: [Webern, Variations Op. 27](https://egorpol.github.io/webern_op27/).
