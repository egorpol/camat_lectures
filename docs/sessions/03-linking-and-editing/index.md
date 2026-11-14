# 3. Building an edition: linking, editing, publishing

Session 3 (double session, 2 × 90 minutes).

In session 2 you saw, mostly on the projector, how an edition links each bar of an encoding to its place on a scan of the print. Today you make an edition yourselves, from the start, and put it online: Edvard Grieg's *Vöglein* (Little bird) from the *Lyric Pieces*, Op. 43 No. 4, two pages of a printed edition. You work in pairs, on one laptop per pair. In block 1 you turn the PDF into page images, find a box around every bar, link the MEI file to both pages, and publish your edition as a repository on GitHub. In block 2 you work on the encoding itself: you read its header, the part that says where the encoding comes from, and restore the slurs, dynamics and pedal marks of one system from the print. Another pair checks your marks against the print. At the end, your edition becomes a live page on the web.

!!! tip "Before the session"
    Your laptop should be set up as in session 2: `02_pdf_preparation.ipynb` prints `CAMAT: 0.2.8`, and VS Code is signed in to your GitHub account. Then get today's notebooks: in your folder `seminar-work`, run `python get_notebooks.py` again (on the cloud route, run your `get_notebooks.ipynb`). It adds the folder `03-linking-and-editing` and keeps everything you already have. If your setup did not work in session 2, don't worry: the first 15 minutes of class are for finishing it, with help.

    To warm up, you can work through `02_live_editing.ipynb` from session 2 at home: you add tempo words and a dynamic to the Schumann piece by hand, and a slur with Copilot. Block 2 works the same way.

**By the end of the session you can**

1. turn the PDF of a printed volume into images of the pages you need, and keep the original file unchanged;
2. describe a page system by system, and check the boxes around its bars;
3. follow the link from a bar in the MEI file to its box on the page, and back;
4. say what the MEI header records and why: where the encoding came from, which print it follows, and who changed what;
5. restore a printed mark in the MEI file and check it against the print and the score;
6. keep an edition in a Git repository, record each change as a commit, and publish it on GitHub as a live page.

**Today in short**

| Part | When | Notebook |
|---|---|---|
| [1. Setup](#1-setup) | block 1, first 15 minutes | |
| [2. The piece: print, scan and encoding](#2-the-piece-print-scan-and-encoding) | block 1 | [`03_grieg_linking.ipynb`](notebooks/03_grieg_linking.ipynb), part 1 |
| [3. Pages and boxes](#3-pages-and-boxes) | block 1 | [`03_grieg_linking.ipynb`](notebooks/03_grieg_linking.ipynb), parts 2–5 |
| [4. Linking the bars to the pages](#4-linking-the-bars-to-the-pages) | block 1 | [`03_grieg_linking.ipynb`](notebooks/03_grieg_linking.ipynb), parts 6–8 |
| [5. Your edition on GitHub](#5-your-edition-on-github) | end of block 1 | [`03_grieg_repository.ipynb`](notebooks/03_grieg_repository.ipynb) |
| [6. The header](#6-the-header) | block 2 | [`03_grieg_editing.ipynb`](notebooks/03_grieg_editing.ipynb), parts 1–3 |
| [7. Restoring the marks of one system](#7-restoring-the-marks-of-one-system) | block 2 | [`03_grieg_editing.ipynb`](notebooks/03_grieg_editing.ipynb), parts 4–5 |
| [8. Peer review](#8-peer-review) | block 2 | [`03_grieg_editing.ipynb`](notebooks/03_grieg_editing.ipynb), part 6 |
| [9. The live page](#9-the-live-page) | end of block 2 | [`03_grieg_live_page.ipynb`](notebooks/03_grieg_live_page.ipynb) |

## 1. Setup

If your setup did not work in session 2, come to the front: we finish it together. Everyone else checks that VS Code is signed in to GitHub (the account icon at the bottom left), runs `get_notebooks.py` as in the tip above, and opens `03_grieg_linking.ipynb`.

**Checkpoint:** each pair has a laptop that prints `CAMAT: 0.2.8` and is signed in to GitHub.

## 2. The piece: print, scan and encoding

As in session 2, keep three things apart:

- **The print.** Volume 1 of Grieg's piano works, published by C. F. Peters in Leipzig with plate number 8800 and edited by Hermann Kretzschmar (the encoding's header dates it 1902). *Vöglein* fills printed pages 42 and 43, with five systems on each page. The print has no bar numbers.
- **The scan.** [IMSLP file 28165](https://imslp.org/wiki/Special:ImagefromIndex/28165): a PDF of 16 pages with all of Op. 43. Our piece is on PDF pages 9 and 10. The notebook downloads it (2.6 MB) and checks that it is exactly the file we prepared the course with.
- **The encoding.** Maja Hartwig and Kristina Richts's MEI file of the piece in the [MEI Sample Collection](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Grieg_Little_bird_Op43_No4.mei). It has the notes and rhythms, the ties, the staccato dots and the accents, but only two dynamics, and no slurs, pedal marks, fingerings or tempo words. We use it as it is: unlike the Schumann file of session 2, nothing was removed on purpose. Block 2 restores some of what is missing.

**Bar numbers.** As the print has none, we use the numbers of the MEI file (its attribute `n`): the short first bar, the *pickup*, is bar 1, and the piece ends with bar 39. Around the two repeat signs, the file counts the two halves of a bar as two bars: bars 9 and 10 on page 42, bars 30 and 31 on page 43. The notebooks, the boxes and the score all use these numbers.

## 3. Pages and boxes

`03_grieg_linking.ipynb` first prepares the pages:

1. it copies PDF pages 9 and 10 into a PDF of their own, `grieg-voglein.pdf`. There they are PDF pages 1 and 2, but their printed numbers stay 42 and 43. The volume itself stays unchanged;
2. it draws both pages as images, at 300 dots per inch. The boxes refer to these images pixel by pixel.

Then, for each page, three steps:

- **Describe the page.** A *system* is the group of staves played together, joined by a brace at the left. You write one line per page that says which bars are on which system, for example `1 | 42 | 1-4, 5-9, 10-14, 15-17, 18-20` (PDF page, printed page, the bars of each system). CAMAT checks the line against the MEI file: it can tell whether every bar is there, in order, but it cannot see where a system ends on the page. Only you can.
- **Find the boxes.** A *box* is a rectangle around one bar, across both staves, given by four numbers in pixels: left, top, right and bottom. You choose one of two ways to find them:
    - **with a chat model** that can read images, such as Copilot Chat in VS Code: the notebook writes the prompt, you attach the page image and save the answer as a file;
    - **with the Edirom measure detector**, a service of the Edirom project that finds the bars on a page image. When you ask it to, the notebook sends the image of one page there, and nothing else.

    If neither works, the notebook uses boxes we saved for the course.

- **Check the boxes.** The notebook draws the page with its boxes, numbered by bar and coloured by system, and compares the number of boxes in each system with your line. Matching numbers do not prove that the boxes are right: look at the pickup, the half bars and the end of each system. If a box is wrong, change its numbers in the box file and save; the picture is redrawn within a second.

Page 42 comes first, step by step. Page 43 repeats the same steps with less help.

## 4. Linking the bars to the pages

When both pages are checked, CAMAT pairs the 39 boxes with the 39 bars, system by system, and draws both pages with the bar numbers on the boxes. You look at both once more and record your names as the reviewers. Then the notebook adds the links to your working file, `work.mei`, together with the page and system breaks of the print, so that the score is drawn with the same systems as the page.

The links form a chain in the MEI file:

- each bar, a `<measure>`, has an attribute `facs` that points to a zone, for example `facs="#zone-grieg-voglein-p0001-020"`. The `#` means "the element with this `xml:id` in the same file";
- the `<zone>` holds the four numbers of the box: `ulx` and `uly` for the upper left corner, `lrx` and `lry` for the lower right;
- the zone sits inside a `<surface>`, one per page, whose `<graphic>` names the page image.

You follow this chain once by hand, for a bar you choose, in `work.mei` with Ctrl+F (Cmd+F on a Mac). Then the other way round, in the score viewer: click a bar and its box lights up on the page; click a box and its bar lights up in the score.

**Checkpoint:** the notebook's check finds no new problems in `work.mei`, all 39 bars point to boxes on two pages, and both pages are reviewed.

## 5. Your edition on GitHub

Your edition is now a folder of files: `work.mei`, the two page images, the boxes and CAMAT's records. `03_grieg_repository.ipynb` turns this folder into a *repository*: a folder whose versions Git records. Each version is a *commit*, a snapshot of all the files with a short message that says what changed, who changed it and when. GitHub keeps a copy of the repository on the web, where anyone can see it.

The notebook writes a description of the edition (`README.md`), the licence of the encoding, and a list of what Git leaves out (the check reports and the PDFs). Then you publish the folder from VS Code with **Publish to GitHub**, as a public repository. The notebook checks that GitHub has your commit and prints a link that opens your file in [mei-friend](https://mei-friend.mdw.ac.at/), an MEI editor in the browser: the score, the file, and page 42 with your boxes. mei-friend finds the page images because they sit next to the MEI file in your repository.

From now on, after each task you record your change as a commit: in VS Code's Source Control view, a message, **Commit**, **Sync Changes**.

!!! note "Your repository is public"
    Anyone can read it, including the names you write into it: in the review of the boxes, in the header and on the review sheet. Use your names, your initials or your GitHub usernames, as you prefer.

**Checkpoint:** your repository is on GitHub, and mei-friend shows your file with page 42.

## 6. The header

`03_grieg_editing.ipynb` continues with the same `work.mei`.

Remember the Schumann piece of session 2: in bars 1 and 5, the encoding has an A3 in the left hand where our print has an F3. Nobody typed it wrong: the encoding was made from another source, a file from the KernScores collection. Its *header* said so, for anyone who read it. The header is the first part of an MEI file, before the music. It describes the work, the sources the encoding follows, and every change made to the file: what, by whom and when. Reusing an encoding saves a lot of typing; the header tells you what you are reusing.

The Grieg header names two sources, our Peters print and a KernScores file, and lists 14 changes over 17 years, from a Humdrum file through MusicXML to MEI 5.1. The notebook shows it in plain words, with the line numbers where you find each part in the file. You add two things:

1. exactly which scan we use: the IMSLP file number and the scan's *fingerprint*, a code computed from every byte of the file (SHA-256), so that anyone can check later that they have the same file;
2. a `<change>` that records your own work today: the links, and the marks you restore.

## 7. Restoring the marks of one system

Each pair restores the marks of one system; your teacher gives you a page and a system. With your system in the print, the score and `work.mei` side by side:

1. **by hand, the dynamics:** letters such as *p* or *pp*, words such as *cresc.*, and *hairpins*, the opening or closing wedges. In the first system of page 42 also the tempo words *Allegro leggiero*;
2. **with Copilot, the slurs:** the notebook writes a prompt with the bars of your system, and you add the first and last note of each slur;
3. **by hand, the pedal marks:** *Ped.* and ✻ under the lower staff.

A mark says where it belongs: in which bar, on which staff and on which *beat*. In 6/8 a bar has six beats, one for each eighth note. The notebook lists the notes of your system with their beats and their `xml:id`s. After each step it lists, in words, what changed in the file, and flags any change outside your task or your system. Notes, rhythms, `xml:id`s and links stay as they are. After each step you also commit and sync.

If you work in the cloud, or Copilot does not answer, you write the slurs by hand; the notebook shows how.

**Extensions:** fingerings; the words *poco ritardando* near the end; the 8va line at the page turn (does the encoding end it where the print does?).

## 8. Peer review

Pairs swap: you review another pair's system on their laptop, and they review yours. For every new mark, compare with the print:

- the right bar and the right beat;
- for a slur, the right first and last note;
- the right staff, above or below;
- nothing changed that should not have.

The notebook shows each changed bar in words and in the print; on GitHub, the other pair's commits show the same changes line by line. The notebook also writes a review sheet with one entry for each change. Under each entry you write **accept**, **correct** (the other pair fixes it while you watch) or **unresolved**, and in a few words why. The sheet goes into the repository too.

A file that passes the notebook's check is valid MEI, but not yet a checked transcription: only the comparison with the print shows that.

**Checkpoint:** every entry on the review sheet has a decision, and the sheet is committed.

## 9. The live page

`03_grieg_live_page.ipynb` writes two files into your repository: `site.json`, which says what the page shows, and a *workflow*, instructions that GitHub follows each time a commit arrives. GitHub then builds the page with CAMAT's site builder and publishes it with GitHub Pages: the score drawn by Verovio with the systems of the print, and the page image beside it. Point at a note and its bar lights up on the page; click it, and the address in the browser becomes a link to that bar.

You switch on GitHub Pages in your repository's settings, commit and sync, and after about a minute your edition is online, at an address of the form `https://your-account.github.io/your-repository/`. Every later commit updates it.

**Checkpoint:** your live page shows the score and the print, with the marks you restored.

## 10. Wrap-up

- Each pair shows its live page: one restored mark and where the print shows it. We discuss the unresolved points from the review sheets.
- An encoding you reuse comes with a header. Read it before you trust the notes, and add to it what you did.
- Boxes, links and marks are checked twice: by the software for their form, by a person against the print.
- A repository keeps every version with its message; a live page shows the current one to anyone.

**Homework**

1. If you did not reach a checkpoint in class, finish that notebook at home. Without boxes of your own, `03_grieg_linking.ipynb` uses the boxes we saved. Then commit and sync, and check that your live page shows your work.
2. Send the link of your live page to your teacher.

## Notebooks

=== "Laptop"

    `python get_notebooks.py` in your folder `seminar-work` copies them into `seminar-work/camat_lectures/03-linking-and-editing/`.

=== "Cloud"

    Your `get_notebooks.ipynb` copies them into `work/camat_lectures/03-linking-and-editing/`. Run them there: the folders they create next to them are then kept too. Parts 5 and 9 need VS Code: do them on your partner's laptop.

All four notebooks work in the folder `grieg_edition_work`, which the first one creates next to itself. Your repository is its subfolder `edition`.

- [`03_grieg_linking.ipynb`](notebooks/03_grieg_linking.ipynb){: download="03_grieg_linking.ipynb" } with [`grieg-edition-inputs.zip`](notebooks/grieg-edition-inputs.zip): parts 2–4. Downloads the scan from IMSLP when you run it.
- [`03_grieg_repository.ipynb`](notebooks/03_grieg_repository.ipynb){: download="03_grieg_repository.ipynb" }: part 5.
- [`03_grieg_editing.ipynb`](notebooks/03_grieg_editing.ipynb){: download="03_grieg_editing.ipynb" }: parts 6–8.
- [`03_grieg_live_page.ipynb`](notebooks/03_grieg_live_page.ipynb){: download="03_grieg_live_page.ipynb" }: part 9.
- For the warm-up at home, from session 2: [`02_live_editing.ipynb`](../02-building-an-edition/notebooks/02_live_editing.ipynb){: download="02_live_editing.ipynb" } with [`schumann-edition-inputs.zip`](../02-building-an-edition/notebooks/schumann-edition-inputs.zip).

Each notebook continues the work of the one before, so run them in this order.

## Sources

- The print: Edvard Grieg, *Lyrische Stücke*, Op. 43, in *Klavierwerke*, vol. 1, ed. Hermann Kretzschmar, Leipzig: C. F. Peters, plate 8800 ([IMSLP file 28165](https://imslp.org/wiki/Special:ImagefromIndex/28165), scanned by piupianissimo; public domain). The notebook downloads it when you run it; it is not part of the course files. The page images in your repository are drawn from it.
- The encoding: Maja Hartwig and Kristina Richts, [*Vöglein* (Little bird), MEI 5.1](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Grieg_Little_bird_Op43_No4.mei), MEI Sample Collection. The file declares itself public domain; the collection is under the [ECL-2.0 licence](https://github.com/music-encoding/sample-encodings/blob/main/LICENSE). We start from it unchanged.
- The saved boxes: found by the [Edirom measure detector](https://measure-detector.edirom.de) and checked by eye.
- The full record of print, scan, encoding and boxes: [`sources.json`](sources/sources.json).
- CAMAT's own guides: [linking a PDF](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_pdf_facsimile_guided.ipynb) and [building a web edition](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_web_edition.ipynb).
