# 2. Building an edition: the source and the notes

Session 2 (double session, 2 × 90 minutes).

In sessions 2 to 4 we build a small digital edition of Robert Schumann's *Fröhlicher Landmann, von der Arbeit zurückkehrend* (*Album für die Jugend*, Op. 68 No. 10). An edition is more than an encoding of the notes: it names the source it follows, links every bar to a scan of that source, records what the editor changed and why, and lets others check it. Today we set up our laptops, look at the source, and get the notes in three ways: from a scan, by typing them, and from an existing encoding.

!!! tip "How to use this page"
    The first block is the setup of your laptop, which we do together with the [setup page](../../setup-laptop.md). If you can, download the installers at home (the setup page says which). No laptop, only a tablet? Then you work in the cloud: choose the tab **Cloud** in part 1. After the setup, the notebooks of this session are ready: see [Notebooks](#notebooks) at the end.

**By the end of the session you can**

1. open and run the seminar notebooks on your own laptop, or in the cloud;
2. tell a printed source, its scan, an encoding and an edition apart;
3. say what optical music recognition (OMR) gives you, and why you still compare it with the scan;
4. type a few notes in ABC and check them against the print;
5. find a bar of the print on the page image and in the MEI file.

**Today in short**

| | What we do | Notebook |
|---|---|---|
| Block 1 | [1. Setup](#1-setup), with [2. Source, scan, encoding, edition](#2-source-scan-encoding-edition) and [3. A wrong note](#3-a-wrong-note) while the downloads run | `02_pdf_preparation.ipynb`, up to the first check |
| Block 2 | [4. From a scan to notes: OMR](#4-from-a-scan-to-notes-omr) | `02_schumann_omr.ipynb` |
| | [5. Typing the notes](#5-typing-the-notes) | `02_note_entry.ipynb` |
| | [6. The page and its bars](#6-the-page-and-its-bars) | `02_pdf_preparation.ipynb` |
| | [7. The note in the MEI file](#7-the-note-in-the-mei-file) | VS Code or JupyterLab |

## 1. Setup

=== "Laptop"

    From this session on, we work on our own laptops. Follow the [setup page](../../setup-laptop.md) step by step, together in class. It installs VS Code (the editor), Miniforge (Python), the seminar's packages, and Git, and connects VS Code to your GitHub account. It ends with a check: the notebook `02_pdf_preparation.ipynb` prints `CAMAT: 0.2.8`.

    Step 4 downloads about 770 MB. While it runs, we look at parts 2 and 3 together.

=== "Cloud"

    If you only have a tablet, or the laptop setup does not work today, you work in the browser: follow the [cloud route](../../setup.md#from-session-2-the-cloud-route). It starts a JupyterLab on Jupyter4NFDI with everything already installed, and ends with the same check: `02_pdf_preparation.ipynb` prints `CAMAT: 0.2.8`. Instead of VS Code you use JupyterLab, and from session 3 on mei-friend.

    There is no big download, so you are ready early. Help a neighbour with the laptop setup, or read parts 2 and 3 ahead.

If something does not work by the end of block 1, we fix it at the start of block 2. Work with a neighbour in the meantime: one working setup per pair is enough for today.

## 2. Source, scan, encoding, edition

Four things that are easy to confuse:

- **The source.** One particular printed edition: Clara Schumann's edition of the *Album für die Jugend*, Leipzig: Breitkopf & Härtel, plate number R.S. 67 (IMSLP dates it 1887). Editors call a source like this a *witness*: it is the evidence of what the music says. Other editions of the same piece differ in details.
- **The scan.** A photograph of one copy of that print, made by the Bavarian State Library and shared on IMSLP as [file 51556](https://imslp.org/wiki/Special:ImagefromIndex/51556): a PDF of 50 pages. No. 10 fills page 8 and has five systems. The print has no bar numbers.
- **The encoding.** The notes as text a computer can read. We start from Maja Hartwig's MEI file of this piece in the [MEI Sample Collection](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei). It was made from another source, not from our print.
- **The edition.** What we make in the next sessions: the encoding, checked against our source, with every bar linked to its place on the scan, our corrections and explanations in the file, and a viewer that shows all this.

## 3. A wrong note

The melody of this piece is in the left hand. In the first full bar, the print has F, A, C, F: dotted quarter, eighth, dotted quarter, eighth. The MEI file from the Sample Collection has A instead of the last F. The same happens in bar 5, where the melody starts again.

| Last bass note of bar 1 and of bar 5 | |
|---|---|
| our print (IMSLP 51556, page 8) | **F3** |
| MEI Sample Collection file | **A3** |
| our starting file for the seminar | **F3**, corrected |

Compare the two files yourself: the same bars from each, with this note in blue. The button *Bar 5* shows the second place.

<div data-demo="compare"
     data-left="https://raw.githubusercontent.com/music-encoding/sample-encodings/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei"
     data-left-title="MEI Sample Collection file"
     data-right="examples/schumann/starter.mei"
     data-right-title="Our starting file"
     data-views="Pickup and bar 1=1-2#d1e338; Bar 5=6-6#d1e1495"></div>

The Sample Collection file also has the tempo words *Frisch und munter* and the dynamic *f*. Our starting file leaves them out on purpose ([part 7](#7-the-note-in-the-mei-file)).

!!! info "Source and licence"
    Left: Maja Hartwig, [*Fröhlicher Landmann*, MEI 5.1](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei), MEI Sample Collection. The file declares itself public domain; the collection is under the [ECL-2.0 licence](https://github.com/music-encoding/sample-encodings/blob/main/LICENSE). The page loads it from GitHub when you open it, and adds the number of staff lines (`lines="5"`), which the file leaves out: without it, Verovio draws no staff lines. Right: our starting file, made from it for this course: [download `starter.mei`](examples/schumann/starter.mei){: download="starter.mei" }. Its header keeps the credits and says what we changed.

We found this because an OMR program (part 4) read F3 where the file has A3. One look at the scan settled it. So an existing encoding saves a lot of typing, but it does not replace the comparison with your source, note by note. That comparison is the core of editing, and the reason an edition links each bar to the scan.

??? info "Pitch names: C4, c′ and kleines c"
    The notebooks use scientific pitch names: middle C is **C4**, and the number goes up at each C. In German (Helmholtz) names:

    | Scientific | C3 | F3 | A3 | C4 | F4 |
    |---|---|---|---|---|---|
    | German | c (kleines c) | f | a | c′ (eingestrichenes c) | f′ |

    The melody of bar 1 is therefore f, a, c′, f.

## 4. From a scan to notes: OMR

Optical music recognition (OMR) is a program that looks at the image of a page and proposes notes. It produces a draft, not a transcription: it can miss notes, misread pitches, merge bars, and it usually drops dynamics and words such as *Frisch und munter*.

Open `02_schumann_omr.ipynb`. It shows what two OMR programs, HOMR and OeMeR, made of our page. We ran them before class (each takes minutes), so the notebook only loads the results.

Both are free, open-source research programs. You start them with a command, not in a window with buttons, and both write their result as MusicXML, a common exchange format for scores.

- **[HOMR](https://github.com/liebharc/homr)** reads photos and scans of printed music. It first finds the staff lines, note heads and bar lines in the image, then reads each staff from left to right with a *transformer*, the same kind of model that language models use. Its documentation says that it concentrates on pitch and rhythm and leaves out dynamics, articulation and other signs. We used version 0.7.0.
- **[OeMeR](https://github.com/BreezeWhite/oemer)** is the older program on which HOMR's first step is based. It sorts every pixel of the image into staff lines, note heads, stems, clefs, rests and so on, and then builds the music from these pieces, step by step. It is meant to cope with photos taken at an angle. We used version 0.1.8.

Other OMR programs work with a window: [Audiveris](https://audiveris.github.io/audiveris/), also free and open source, shows what it recognised on top of the scan, lets you correct it, and then exports MusicXML. Commercial programs work the same way.

1. Look at the scan next to HOMR's result for the first two systems.
2. Compare bar 1 and bar 5 in the bass: which pitch does HOMR read at the end of each bar?
3. Find one thing HOMR got wrong or left out.

??? note "Extension: OeMeR and running OMR yourself"
    Part 4 of the notebook shows OeMeR on the whole page: it reads most of the right hand in the bass clef, finds 19 bars instead of 21 and loses the C3 of the pickup. Part 5 runs both programs again; that needs extra installations and several minutes per page.

    Without installing anything, you can try HOMR on its [demo website](https://homr.site): upload a picture of a page (JPG or PNG; a screenshot of page 8 of the scan works) and download the MusicXML. Open it in the *Any format* box in part 5 to see what HOMR read. The website does not say who runs it, so upload only pages you may share, such as our public-domain scan.

## 5. Typing the notes

The other way to get notes is to type them. Type the bass melody of the pickup and bar 1 in ABC, as in session 1:

- pickup: C3, eighth
- bar 1: F3 dotted quarter, A3 eighth, C4 dotted quarter, F3 eighth

The piece is in F major (one flat), in common time, in the bass clef. The box below has the header and the pickup already; type bar 1 after the bar line. Three things you need in ABC:

- `L:1/8` makes the eighth note the unit: `G,` is an eighth, `G,2` a quarter, `G,3` a dotted quarter.
- A comma puts a note one octave lower: `C` is C4 (middle C), `C,` is C3.
- `|` is a bar line; `|]` ends the piece.

<div data-demo="edit" data-file="examples/schumann/pickup-bar1.abc" data-format="abc" data-title="ABC"></div>

The score changes as you type. Compare it with the print: pitches and octaves, rhythm, pickup, clef and key. Under the score, *Verovio reads* lists the notes in words, so you can check them against the list above. The same exercise is part 1 of `02_note_entry.ipynb`; you can also [download the box's starting text](examples/schumann/pickup-bar1.abc){: download="pickup-bar1.abc" }.

??? success "Solution"
    ```text
    C, | F,3 A, C3 F, |]
    ```

Then think about the whole piece: 21 bars on two staves. What does an existing encoding save you, and what does it not?

### Two more ways in

Typing an encoding sign by sign is slow for a whole piece. There are two other ways to get the same five notes into the computer. Try one if you have time; the *Any format* box below the tabs shows the result of either.

=== "A notation program: MuseScore"

    [MuseScore](https://musescore.org) is a free notation program: you enter notes with the mouse, the computer keyboard or a MIDI keyboard and see the score as you go, as in Sibelius, Finale or Dorico. It is not part of our setup; [download it](https://musescore.org/en/download) if you want to try.

    1. Create a score with one bass-clef staff (or a piano) in F major, 4/4, with an eighth-note pickup ([how to make a pickup bar](https://handbook.musescore.org/notation/rhythm-meter-and-measures/pickup-and-non-metered-measures)).
    2. Enter the five notes.
    3. Choose **File → Export** and save the score as **MEI** (MuseScore 4.2 or newer) or as uncompressed **MusicXML** (`.musicxml`) ([exporting](https://handbook.musescore.org/file-management/file-export)).
    4. Click **Open a file** in the box below and choose the exported file. It is read in your browser; nothing is uploaded.

    A notation program is the quickest way to enter many notes. Once an edition has links to the scan and editorial notes, though, we edit its MEI directly: a round trip through a notation program can lose them.

=== "A language model"

    A language model can turn notes written in words into an encoding. Write the notes the way you think of them, in English, in German or as letters, and ask for ABC or MEI. For example:

    ```text
    Write these notes in ABC notation and answer with the ABC only.
    Schumann, Fröhlicher Landmann, left hand.
    F major, common time, bass clef.
    Pickup: C3 eighth.
    Bar 1: F3 dotted quarter, A3 eighth, C4 dotted quarter, F3 eighth.
    ```

    Use Copilot's chat in VS Code (setup, step 6) or any chat assistant in your browser. Paste the answer into the box below; it does not matter if the answer comes inside a code block. Then check it as in session 1: pitches and octaves, lengths, pickup, clef and key. Ask again for MEI instead of ABC, and compare.

<div data-demo="edit" data-format="auto" data-title="Any format"></div>

The box finds out which format the text is in, draws the score and lists what Verovio reads. **Show as MEI** shows the same notes as MEI: that is how a result from MuseScore or a language model can become part of an MEI edition.

??? note "Extension: three more text formats"
    Part 2 of `02_note_entry.ipynb` has the same five notes in Plaine & Easie, in MEI written by hand and in kern. You can paste each of them into the *Any format* box too. Compare your result with a neighbour who used another format.

## 6. The page and its bars

Continue `02_pdf_preparation.ipynb` from the check where the setup stopped. The notebook

1. downloads the scan and keeps it unchanged;
2. copies page 8 into a one-page PDF (in that file it is page 1, but its printed number stays 8);
3. draws the page as an image, which is what we link the bars to next session;
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

Our edition covers the pickup and bars 1–8: the first two systems.

## 7. The note in the MEI file

Now find the wrong note from part 3 in the encoding. First in the score: here are the pickup and bar 1 of our starting file, with the F3 at the end of bar 1 selected. Click or tap any other note or rest, then come back to the F3.

<div data-demo="inspect" data-file="examples/schumann/starter.mei" data-range="1-2" data-note="d1e338"></div>

Under the score you see the selected note three times: in words, as its line in the MEI file, and as the group of shapes that Verovio drew for it (notehead, stem, flag). The MEI line and the drawing carry the same identifier, here `d1e338`. That is how the drawing knows which note it shows. The pitch and the length, however, are only in the MEI file: the drawing only knows where to put its shapes.

??? info "What is SVG?"
    Verovio draws scores as SVG (Scalable Vector Graphics): a picture described as text, such as "a circle here, this big, in this colour". Because the picture is text, it stays sharp at any size, and a program can find one note in it by its identifier. The [SVG introduction](examples/svg-introduction/index.html) shows a circle written as text, the same note symbol enlarged as pixels and as SVG, and the pickup note as MEI and as SVG. We use SVG again next session, when we link the score to the scan.

Now find the same note in the file itself:

=== "Laptop"

    1. In VS Code's file list on the left, open the folder `schumann_edition_work` next to the notebook, then `inputs`, then the one folder inside it (its name is a code, such as `b02b5197b383`), and click `starter.mei`. This is our starting file.
    2. Press ++ctrl+f++ (macOS: ++cmd+f++) and type `"d1e338"`, with the quotation marks.

=== "Cloud"

    1. In JupyterLab's file browser, open `work` → `camat_lectures` → `02-building-an-edition` → `schumann_edition_work` → `inputs` → the one folder inside it (its name is a code, such as `b02b5197b383`), and double-click `starter.mei`. This is our starting file; it opens as text.
    2. Choose *Edit → Find…*, type `"d1e338"`, with the quotation marks, and click the arrow pointing down (*Next Match*) next to the search field.

You land on `<note xml:id="d1e338" pname="f" oct="3" dur="8" .../>`: the last bass note of bar 1, F3, an eighth. Scroll up to the `<measure n="2" ...>` it belongs to. Without the quotation marks, the search first finds the same ID in the file's header, where our correction is described.

Every note in the file has such an `xml:id`. It is how the drawing, the scan links and your corrections point at exactly this note, and how you can name it to a language model next session. HOMR's MusicXML and your ABC from part 5 have no such identifiers. Do not change the file yet: next session we edit a copy of it.

??? note "Extension: the same note in mei-friend"
    [Open the MEI Sample Collection's file in mei-friend](https://mei-friend.mdw.ac.at/?file=https://raw.githubusercontent.com/music-encoding/sample-encodings/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei&select=d1e338), the editor we use from session 3 on. Click **Got it!** if a welcome box appears. The link selects this note: it is blue in the score, and the code on the right shows its line. There it is still `pname="a"`, the A3 from part 3.

??? info "Why does the starting file have no slurs or dynamics?"
    We removed the slurs, dynamics, tempo words and articulation from Maja Hartwig's file on purpose. Restoring some of them from the print is one of the editing tasks in session 3. The file's header says exactly what was removed.

## 8. Wrap-up

- Source, scan, encoding and edition are four different things. The source is the evidence; everything else is checked against it.
- OMR and existing encodings save typing. Neither saves the comparison with the source.
- Next session: we link each bar to its place on the page image, then correct and add to the encoding by hand and with Copilot. In session 4, we put the edition on GitHub and publish it.

**Homework**

1. If the setup did not finish in class, complete it with the [setup page](../../setup-laptop.md) until the check prints `CAMAT: 0.2.8`. If your laptop setup is stuck, use the [cloud route](../../setup.md#from-session-2-the-cloud-route) for now. If you get stuck, write down the step and the error message and bring them next time.
2. Compare the bass of bars 2–4 in the print with what HOMR read (`02_schumann_omr.ipynb`). Note one difference, if you find one.

## Notebooks

=== "Laptop"

    The last step of the setup copies the notebooks into `seminar-work/camat_lectures/02-building-an-edition/`.

=== "Cloud"

    Step 3 of the cloud route copies the notebooks into `work/camat_lectures/02-building-an-edition/`. Run them there: the folders they create next to them are then kept too.

Two of them need a ZIP file with data next to them; the download script copies those too.

- [`02_pdf_preparation.ipynb`](notebooks/02_pdf_preparation.ipynb){: download="02_pdf_preparation.ipynb" } with [`schumann-edition-inputs.zip`](notebooks/schumann-edition-inputs.zip): parts 1 and 6. Downloads the scan from IMSLP when you run it. Next session continues in the folder `schumann_edition_work` that it creates.
- [`02_schumann_omr.ipynb`](notebooks/02_schumann_omr.ipynb){: download="02_schumann_omr.ipynb" } with [`schumann-omr-recordings.zip`](notebooks/schumann-omr-recordings.zip): part 4.
- [`02_note_entry.ipynb`](notebooks/02_note_entry.ipynb){: download="02_note_entry.ipynb" }: part 5. No ZIP needed.

## Sources

- The print: Robert Schumann, *Album für die Jugend*, Op. 68, ed. Clara Schumann, Leipzig: Breitkopf & Härtel, plate R.S. 67 ([IMSLP work page](https://imslp.org/wiki/Album_f%C3%BCr_die_Jugend,_Op.68_(Schumann,_Robert)), [file 51556](https://imslp.org/wiki/Special:ImagefromIndex/51556); scan: Bayerische Staatsbibliothek). The notebooks download it when you run them; it is not part of the course files.
- The encoding: Maja Hartwig, [*Fröhlicher Landmann*, MEI 5.1](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei), MEI Sample Collection. The file declares itself public domain; the collection is under the [ECL-2.0 licence](https://github.com/music-encoding/sample-encodings/blob/main/LICENSE). Our starting file keeps its credits.
- The full record of source and encoding: [`sources.json`](sources/sources.json).
- OMR programs: [HOMR](https://github.com/liebharc/homr), [OeMeR](https://github.com/BreezeWhite/oemer).
- A finished facsimile-linked edition: [Webern, Variations Op. 27](https://egorpol.github.io/webern_op27/).
