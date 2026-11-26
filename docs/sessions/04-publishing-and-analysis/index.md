# 4. The class edition, first analysis

Session 4 (double session, 2 × 90 minutes).

In session 3 each pair restored the marks of one system of Grieg's *Vöglein* and published its edition as a live page. Today the class puts its work together and starts to read the music as data. In block 1 a notebook fetches every pair's edition from GitHub and joins the systems into one file, the *class edition*. A table shows who restored which system, and which systems nobody did. Then you take the first counts: notes per bar, a piano roll, the most common pitches and note lengths, and the marks in each bar. In block 2 you go back to your pair's own edition. The computer searches the piece for the bird call of bar 1, and you decide, by looking at the score and the print, which of its hits really are the call. One of them becomes your finding: a short note in your edition that your live page shows below the score.

!!! tip "Before the session"
    Your edition from session 3 should be on GitHub, with its live page online. If it is not, finish session 3's homework first. Then get today's notebooks: in your folder `seminar-work`, run `python get_notebooks.py` again (on the cloud route, run your `get_notebooks.ipynb`). It adds the folder `04-publishing-and-analysis` and keeps everything you already have. Work where you finished session 3, and leave your session-3 folder where it is: today's notebooks find `grieg_edition_work` in the folder `03-linking-and-editing` next door. Your copy on GitHub is not enough, because the notebooks also use files that only that folder holds.

    To warm up, you can open `01_binary_grid.ipynb` from session 1 again: the search in block 2 works on the same kind of grid.

**By the end of the session you can**

1. join the work of several pairs into one edition, and say which system came from which pair and which systems have no marks from the class;
2. say why a count of marks depends on who restored what, and not only on the music;
3. read a note table, a piano roll and a few simple counts, and say what each one can and cannot show;
4. search a piece for a short figure, at the printed pitch and at every pitch, and follow a hit back to the score and the print;
5. tell a repeat, a step of a sequence and a false hit apart, with a reason you can point to in the music;
6. add a finding to your edition that points at the notes it is about, and see it on your live page.

**Today in short**

| Part | When | Notebook |
|---|---|---|
| [1. The class list](#1-the-class-list) | block 1, first 10 minutes | [`04_class_edition.ipynb`](notebooks/04_class_edition.ipynb), part 1 |
| [2. The class edition](#2-the-class-edition) | block 1 | [`04_class_edition.ipynb`](notebooks/04_class_edition.ipynb), parts 2–3 |
| [3. Other versions, one system beside the print](#3-other-versions-one-system-beside-the-print) | block 1 | [`04_class_edition.ipynb`](notebooks/04_class_edition.ipynb), parts 4–5 |
| [4. Counting notes and marks](#4-counting-notes-and-marks) | second half of block 1 | [`04_class_edition.ipynb`](notebooks/04_class_edition.ipynb), parts 6–7 |
| [5. The bird call](#5-the-bird-call) | block 2, first 10 minutes | [`04_pattern_search.ipynb`](notebooks/04_pattern_search.ipynb), part 1 |
| [6. Searching for the call](#6-searching-for-the-call) | block 2 | [`04_pattern_search.ipynb`](notebooks/04_pattern_search.ipynb), parts 2–3 |
| [7. Sorting your hits](#7-sorting-your-hits) | block 2 | [`04_pattern_search.ipynb`](notebooks/04_pattern_search.ipynb), part 4 |
| [8. Your finding on the live page](#8-your-finding-on-the-live-page) | end of block 2 | [`04_pattern_search.ipynb`](notebooks/04_pattern_search.ipynb), part 5 |

## 1. The class list

At the end of session 3 you sent your teacher the link to your live page. From those links your teacher made a *class list*: one row per pair, with the page and the system you restored, your repository, and the commit to use. The commit fixes the version: what you change in your repository later does not change the class edition.

When several pairs restored the same system, your teacher picked one version for the class edition: its row says `yes` under `use`. The other versions come back in part 3, as a comparison against the print.

Open `04_class_edition.ipynb` and run the setup cells at the top with Shift+Enter: the third one finds your folder `grieg_edition_work`. The next cell, `CLASS_LIST`, starts with one example row. Paste the whole list your teacher hands out between the triple quotes `"""`, with its first line of column names, in place of the example, and run the cell. The list holds your GitHub usernames, so it is shared in class only.

## 2. The class edition

Each pair's `work.mei` holds the marks of one system. To count marks across the whole piece, they have to be in one file. The notebook:

1. downloads each pair's `work.mei` and review sheet from GitHub, as they were at the commit on the list. It keeps what it has downloaded: when you run it again, it only fetches what is still missing;
2. starts from your own file as it was before you restored the marks, with its links to the pages (`edition/checkpoints/before-editing.mei`);
3. copies each system's marks from the pair that restored it. First it checks that the notes in that pair's file are still those of the encoding: a pair whose notes changed is reported and left out. Marks outside a pair's own system, and other changes, are listed and not copied.

The result, `class-edition.mei`, goes into a new folder `class_edition` inside `grieg_edition_work`. It sits beside your repository `edition`, not inside it: it is the class's file, not your pair's, and it is not published.

The *coverage table* has one row per system and says what happened to it:

- **merged**: the system's marks are in the class edition, from the pair named in the row, with the number of marks that pair added, changed or removed;
- **gap**: no pair restored this system. It keeps only the marks the encoding already had;
- a system that could not be used (not fetched, notes changed, several versions and none picked) says so.

Above the table, the notebook says why a system could not be used, and lists any of a pair's changes that it did not copy.

The table also counts the entries on each pair's review sheet that have a decision. A complete sheet can still hold *unresolved* entries: a reviewed system is not yet a correct one.

**Checkpoint:** everyone has the class edition and can say which systems came from which pair, and which have no marks from the class.

## 3. Other versions, one system beside the print

Where several pairs restored the same system, the notebook lists how each other version differs from the picked one. Look up each difference in the print: which reading do you prefer, and why?

Then choose a system that the coverage table calls merged, and put its page and system into the cell `show_class_system(GRIEG, 42, 1)` in place of `42` and `1`. The notebook draws its bars from the class edition, with the MEI bar numbers, and beside them the same bars of the page, cut out with your boxes from session 3. For each kind of mark that the coverage table names for that system, find one in the score and in the print.

## 4. Counting notes and marks

Open the class edition in CAMAT and work through the cells with your partner.

- **Two tables.** `df_pitch` holds the notes. `df_events` holds rests, clefs and marks. Follow the slur in MEI bar 2 from the events table to the notes at its ends.
- **Notes per bar.** Count the notes in each MEI bar. Where are the highest and the lowest note?
- **Piano roll and selection.** Each note is a strip at its pitch, as long as the note lasts. Look at the whole piece, then pick the upper staff in MEI bars 1–4.
- **Pitch, note length and pitch class.** Which pitches and note lengths come most often in the selection and in the whole piece? A pitch class counts notes such as C4 and C5 together.
- **Marks per bar.** How many dynamics, slurs, hairpins and other marks sit in each MEI bar? Staccato dots and accents are not counted here. Bars of systems the class did not merge are shaded.

**Reading the numbers.** The plots count what is in the file. A gap keeps only the encoding's marks: *p* in bar 1, *pp* in bar 10, the staccato dots and the accents, the 8va line in bar 20. So a bar with many marks may simply belong to a system a pair restored. The counts describe the class's selection, not yet the whole piece.

**Question for block 2.** The bird call of bar 1 comes back later in the piece. How often? How exactly: with the same pitches and the same rhythm, or higher or lower? And can the computer tell a repeat from an imitation?

If you have time, follow one melodic line to see which pitches come next, how far they move and where notes start in each bar.

## 5. The bird call

`04_pattern_search.ipynb` works on your pair's own edition again, `edition/mei/work.mei`, with the bar numbers of session 3. Bar 1, the pickup, holds the start of the bird call: a quick figure of thirty-second notes in both hands that lands on an eighth note at the start of bar 2, ten notes in all. The notebook highlights it in the score; find it on the scan too.

Three words for how a figure can come back:

- a **repeat** brings it back with the same rhythm and the same intervals, the distances between its pitches;
- a **transposition** moves all its pitches up or down by the same distance;
- a **sequence** repeats its shape at new pitches, step by step. A step can keep the rhythm and the shape and still change some intervals.

The search works on a grid, like the binary grid of session 1: each row is a pitch, each column is the length of a thirty-second note, and a dark cell means that the pitch is sounding. On the grid, the call's ten notes fill 16 dark cells. The search slides the call's grid along the piece and gives each place a *score*: the share of the call's dark cells that are dark there too. A score of 1.0 means all 16.

## 6. Searching for the call

- **At the printed pitch.** First the call's grid keeps its own pitch. One cell runs the search with CAMAT's own functions: `parse_files` reads your edition into `df_pitch`, a piano roll shows bars 1–5, and `search_binary_query` slides the call's grid along the piece. The search keeps the hits with a score of 0.75 or more. A *heatmap* shows the score at every place the grid was tried, with the hits as numbered circles. The next cell numbers them from the highest score down, and in the order of the piece where scores are equal. You follow hit 2 to the score and the scan.
- **At every pitch.** Then the grid may move up and down by any number of *semitones* (a semitone is the step from one key of the piano to the next, black keys included). The notebook numbers the hits again, in a new table. New hits appear: one in bars 6–7 with a score of 1.0, and many with a score of 0.75, which fill 12 of the call's 16 cells. Some of them sound like the call, others do not. CAMAT's heatmap now has one row for each pitch shift.

A score counts cells, not music. A held note fills the same cells as the same note repeated, and extra notes do not lower the score. Even a score of 1.0 only says that all the call's cells are filled.

**Checkpoint:** you can find hit 2 and the hit in bars 6–7 in the score and on the scan, and read their scores and pitch shifts.

## 7. Sorting your hits

Your teacher gives your pair three hit numbers from the table *at every pitch*. Put them into `MY_HITS` in place of the three example numbers, and run the cell. If the notebook warned that your notes differ from the source, your numbers may point at other passages: check the bars with your teacher. For each hit, look at the score and the scan: follow the rhythm, the shape of the pitches and the landing note. CAMAT also lays the hit's grid next to the call's and marks the cells that are missing. Decide together which kind it is:

- a **repeat**: the call again, with the same rhythm and intervals, at its own pitch or transposed;
- a **sequence step**: one step of a sequence, the call's shape at new pitches with some intervals changed;
- a **false hit**: the cells line up, but the music does something else.

For each choice, give one reason that you can point to in the music.

**Checkpoint:** each of your hits has a kind and a reason.

## 8. Your finding on the live page

Choose one of your three hits for your *finding*: a short note in your edition about this passage, which your live page shows below the score.

1. Put its number into `MY_HIT` and run the cell. The notebook drafts a first sentence with the search facts: the bars, the pitch shift, and how many of the call's cells match. Check it against the score and the scan.
2. In the next cell, put the kind into `MY_CATEGORY`: `"repeat"`, `"sequence-step"` or `"false-hit"`. In `MY_SENTENCE`, write one sentence of your own between the quotes: what does the search score miss in this passage?
3. Run the cell. It saves both sentences in `work.mei`, linked to the matched notes. When you run it again, it replaces your finding and never adds a second one. Then it builds a test copy of your live page on your laptop. Go on when it prints a line starting with `✓ test build`; if a line starts with ✗, read it first.

??? info "What does the notebook write into `work.mei`?"
    An `<annot>`, MEI's element for a note by the editors, in the bar of the first matched note. Its attribute `label` holds the kind you chose. Its attribute `plist` lists the matched notes, each as `#` and the note's `xml:id`: the same kind of link as a bar's `facs` in session 3.

Then publish it as in session 3: in VS Code, open the Source Control view of your `edition` folder, write the message *Add our finding*, click **Commit**, then **Sync Changes**. In your repository's **Actions** tab on GitHub, wait until the *Live page* run shows a green tick, after about a minute. The notebook's last cell checks that GitHub has your commit and that your live page shows the finding, and prints a link. If it says the page is not ready yet, wait a minute and run the cell again. On the page, below the score, click your finding under **Editorial notes**: its notes light up in the score. If the page still shows the old version, reload it with Ctrl+Shift+R (Cmd+Shift+R on a Mac).

!!! note "Your finding is public"
    Like everything in your repository, your finding can be read by anyone. Write it as a short note for a reader of the edition.

**Checkpoint:** your live page lists your finding and lights up its notes.

## 9. Wrap-up

- Two pairs read their finding aloud and show its notes on their live page.
- Joining the class's work needs a record of who did what: the coverage table. The counts are only as complete as that coverage.
- A plot counts what is in the file. What a number means, you find out in the score and the print.
- A search score says how many cells line up, not that the music is the same. You decided the kind of each hit by looking at the music.
- A finding names its passage and says what the evidence does not show.

**Extension:** the last box of `04_pattern_search.ipynb` gives one line to paste into a new cell. It searches across octaves: all Cs share one row, all C-sharps another, and so on. Which passages turn up when the octave no longer counts?

**Homework**

1. If you did not reach a checkpoint in class, finish that part at home. If it was your finding, commit and sync it, and check that your live page shows it.

## Notebooks

=== "Laptop"

    `python get_notebooks.py` in your folder `seminar-work` copies them into `seminar-work/camat_lectures/04-publishing-and-analysis/`.

=== "Cloud"

    Your `get_notebooks.ipynb` copies them into `work/camat_lectures/04-publishing-and-analysis/`. Part 8 adds your finding to your pair's repository and needs VS Code to commit and sync: work on the laptop where you published your edition in session 3.

Both notebooks work in your session-3 folder `grieg_edition_work`: the first adds the folder `class_edition`, the second adds your finding to `edition/mei/work.mei`.

- [`04_class_edition.ipynb`](notebooks/04_class_edition.ipynb){: download="04_class_edition.ipynb" }: parts 1–4. Downloads the pairs' files from GitHub when you run it.
- [`04_pattern_search.ipynb`](notebooks/04_pattern_search.ipynb){: download="04_pattern_search.ipynb" }: parts 5–9.
- For the warm-up, from session 1: [`01_binary_grid.ipynb`](../01-why-encode-music/notebooks/01_binary_grid.ipynb){: download="01_binary_grid.ipynb" }.

## Sources

- The print and the encoding are the same as in session 3: see [its sources](../03-linking-and-editing/index.md#sources).
- The marks in the class edition come from the pairs' own repositories on GitHub, at the commits on the class list.
- CAMAT's own guides: [reading an MEI file as tables](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_parse_tables.ipynb), [searching with a binary grid](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/binary_pattern_search.ipynb) and [comparing searches in heatmaps](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/chord_progression_search.ipynb).
