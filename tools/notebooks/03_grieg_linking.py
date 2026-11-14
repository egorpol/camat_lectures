# %% [markdown]
# # From the PDF to a linked MEI file
#
# Session 3, *Linking and editing*: block 1.
#
# In session 2 you saw how each bar of an MEI file can point to the place on a page where it is printed. Today you make these links yourself, from the start, for a piece of two pages: Edvard Grieg's *Vöglein* (Little bird), Op. 43 No. 4.
#
# By the end of this notebook you have:
#
# - the printed volume from IMSLP, unchanged, and our two pages in a PDF of their own;
# - both pages as images, each described system by system;
# - a box around each of the 39 bars, checked by you;
# - your working file `work.mei`, in which every bar points to its box.
#
# Keep `grieg-edition-inputs.zip` in the same folder as this notebook (`get_notebooks.py` puts it there). The notebook works in the folder `grieg_edition_work` next to it. Your MEI file is `grieg_edition_work/edition/mei/work.mei`; open it in the editor when the notebook says so.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong, the message appears under the cell.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed; after the setup they already are, so it finishes quickly. The second cell defines helper functions; it is collapsed because you do not need to read it. The third checks that everything is there: it prints `CAMAT: 0.2.8` and `pypdf: 6.10.0`.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: grieg_linking

# %%
import importlib.metadata
from camat.pdf_facsimile import check_poppler

check_poppler()
print("CAMAT:", importlib.metadata.version("camat"))
print("pypdf:", importlib.metadata.version("pypdf"))

# %% [markdown]
# ## 1. The encoding and the print
#
# **The encoding** comes from the [MEI Sample Collection](https://github.com/music-encoding/sample-encodings): Maja Hartwig and Kristina Richts encoded the piece in Detmold. It has the notes and rhythms, the ties, the staccato dots and accents, but almost no dynamics and no slurs or pedal marks. We come back to that in block 2.
#
# **The print** is volume 1 of Grieg's piano works, published by C. F. Peters in Leipzig: [IMSLP file 28165](https://imslp.org/wiki/Special:ImagefromIndex/28165). The PDF has 16 pages, all of Op. 43; our piece is on PDF pages 9 and 10, which are printed pages 42 and 43.
#
# The next cell
#
# 1. unpacks the encoding and our settings into `grieg_edition_work/inputs`, and copies the encoding to your working file `work.mei`;
# 2. downloads the volume (2.6 MB) into `grieg_edition_work/sources` and keeps it unchanged.
#
# It also checks that the download is exactly the file we prepared the course with. If the download does not work, copy the PDF from the USB stick to the place the message names, and run the cell again.
#
# <details><summary>How can a notebook tell that two files are the same?</summary>
#
# It computes a *fingerprint* (a SHA-256 hash) from every byte of the file: a code of 64 letters and digits. If a single byte differs, the code is completely different. The notebook compares the code of your download with the one we recorded.
#
# </details>

# %%
PROJECT = Path.cwd() / "grieg_edition_work"
GRIEG = load_inputs(PROJECT)
WORK_MEI = GRIEG["work"]
get_volume(GRIEG)

# %% [markdown]
# ## 2. Cut out our two pages
#
# We need only two pages of the volume. The next cell copies PDF pages 9 and 10 into a PDF of their own, `grieg-voglein.pdf`. In that file they are PDF pages 1 and 2, but their printed page numbers stay 42 and 43. The volume itself stays as it is: the copy is a new file, made from it.
#
# Three numbers for the same page can be confusing. From here on, *PDF page* means a page of our two-page PDF, and *printed page* the number printed at the top of the page.

# %%
cut_pages(GRIEG)

# %% [markdown]
# ## 3. The pages as images
#
# CAMAT draws each page of our PDF as a PNG image at 300 dpi (dots per inch): 2717 × 3496 pixels. It writes down how it made the images in `edition/pages/pages.json`. The boxes refer to these images pixel by pixel, so the images must stay exactly as they are. The notebook shows them smaller.

# %%
draw_pages(GRIEG)

# %% source-media
show_pages(GRIEG)

# %% [markdown]
# ### Bars and their numbers
#
# The print has no bar numbers. We use the numbers of the MEI file, its `n`: the short first bar, the *pickup*, is bar 1, and the piece ends with bar 39.
#
# Around the repeat signs, the MEI file counts the two parts of a bar separately. On page 42, bar 9 is the half bar that ends the second system, before the repeat sign `:‖`, and bar 10 is the half bar after `‖:` at the start of the third system. On page 43 the same happens with bars 30 and 31. So "bar 10" in this session always means the MEI's bar `n="10"`.

# %% [markdown]
# ## 4. Page 42: describe it, find its boxes, check them
#
# ### 4a. Describe the page
#
# A *system* is the group of staves played together, joined by a brace at the left. Page 42 has five systems. CAMAT needs to know which bars are on which system. We write that as one line per page:
#
# `PDF page | printed page | bars of each system`
#
# The systems are separated by commas; `1-4` means bars 1 to 4. Check the line in the next cell against the picture above: count the bars of each system, with the half bars 9 and 10 around the repeat sign. Then run the cell. CAMAT checks the line against the MEI file: every bar once, in the right order. Page 43 is not described yet, so bars 21–39 are still open: that is expected.

# %%
PAGE_42 = "1 | 42 | 1-4, 5-9, 10-14, 15-17, 18-20"

describe_page(GRIEG, PAGE_42, 1)

# %% [markdown]
# **Extension: what the check can see, and what it cannot.** The next cell tries two wrong lines, without saving them. The first leaves out bar 5 and is rejected. The second ends the second system one bar too early, and is accepted: CAMAT cannot see where a system ends on the page. Only a look at the image shows that mistake.

# %%
describe_page(GRIEG, "1 | 42 | 1-4, 6-9, 10-14, 15-17, 18-20", 1, save=False)
print()
describe_page(GRIEG, "1 | 42 | 1-4, 5-8, 9-14, 15-17, 18-20", 1, save=False)

# %% [markdown]
# ### 4b. Find the boxes
#
# A *box* is a rectangle around one bar, in both staves. It is four numbers, in pixels of the page image: **left** and **top** for its upper left corner, **right** and **bottom** for its lower right corner. In the file they are called `ulx`, `uly` (upper left x and y) and `lrx`, `lry` (lower right). x counts from the left edge of the page, y from the top edge, so y grows downwards.
#
# There are two ways to find the boxes. Choose one.
#
# **With a chat model.** A chat model that can read images (in VS Code: Copilot Chat, with a model that accepts images) can give the boxes directly. The next cell names the image to attach and prints a prompt to copy. Save the model's answer as the file the cell names: in VS Code, *File → New Text File*, paste the answer, *File → Save As* under that name. Then run the cell after it, with `SEND_TO_DETECTOR = False`. Chat models make mistakes; the check in 4c shows them.
#
# **With the Edirom measure detector.** The Edirom project runs a service that finds the bars on a page image: [measure-detector.edirom.de](https://measure-detector.edirom.de). Write `SEND_TO_DETECTOR = True` in the cell after next and run it. The notebook sends the image of page 42 there, and nothing else, and saves the answer as the box file.
#
# If neither works, run the cell with `SEND_TO_DETECTOR = False` and without a box file: it then uses the boxes we saved for the course.

# %%
box_prompt(GRIEG, 1)

# %%
SEND_TO_DETECTOR = False   # True sends the image of page 42 to the Edirom measure detector

find_boxes(GRIEG, 1, send=SEND_TO_DETECTOR)

# %% [markdown]
# ### 4c. Check the boxes
#
# The next cell shows page 42 with its boxes. Each box is labelled with the bar it will point to, and coloured by its system. CAMAT does not read the music: it pairs boxes and bars by their order, system by system, from left to right. Above the picture it compares the number of boxes in each system with the bars of your line (4, 5, 5, 3 and 3).
#
# Matching numbers do not show that the boxes are right; only looking does. Look closely at the pickup (bar 1), at the half bars 9 and 10 around the repeat sign, and at the last bar of each system.
#
# The picture follows the box file. Open the file in the editor (the cell above names it), change one number and save (Ctrl+S, on a Mac Cmd+S): within a second the picture is drawn again. If a box is wrong, correct its numbers this way. To try it with a correct file, make one box much narrower, look, then undo (Ctrl+Z) and save again.

# %% source-media
watch_boxes(GRIEG, 1)

# %% [markdown]
# To find a box in the file, the next cell lists each bar with the position of its box in the file (counted from 1) and its four numbers.

# %%
list_boxes(GRIEG, 1)

# %% [markdown]
# ## 5. Page 43: the same three steps
#
# Now page 43, with less help.
#
# 1. **Describe the page.** Write its line between the quotation marks, in the same form as for page 42. It is PDF page 2. Its first bar is bar 21; bars 30 and 31 are the half bars around the second repeat sign. If you leave the line empty, the notebook uses ours.
# 2. **Find the boxes**, with the chat or the detector.
# 3. **Check them** in the picture.

# %%
PAGE_43 = ""   # for example "2 | 43 | ..."

describe_page(GRIEG, PAGE_43, 2)

# %%
box_prompt(GRIEG, 2)

# %%
SEND_TO_DETECTOR = False   # True sends the image of page 43 to the Edirom measure detector

find_boxes(GRIEG, 2, send=SEND_TO_DETECTOR)

# %% source-media
watch_boxes(GRIEG, 2)

# %% [markdown]
# ## 6. Link both pages
#
# ### 6a. Pair the boxes with the bars
#
# The next cell checks both page lines together against the MEI file, then lets CAMAT pair the 39 boxes with the 39 bars, system by system. It stops if a system has more or fewer boxes than bars. CAMAT then draws both pages with the boxes as it paired them: its labels read `1/20`, movement 1, bar 20.

# %% source-media
align_pages(GRIEG)

# %% [markdown]
# ### 6b. Record your review
#
# Look at both pictures once more, then write your names between the quotation marks and run the cell. CAMAT records who checked the boxes of each page, and when. If the boxes change later, it resets the review. At the end of this block your edition goes into a public repository on GitHub, with this record: names, initials or GitHub usernames are all fine.

# %%
REVIEWED_BY = ""   # for example "Anna and Ben"

record_review(GRIEG, REVIEWED_BY)

# %% [markdown]
# ### 6c. Add the links to the MEI file
#
# If `work.mei` is open in the editor, save it first. Then run the next cell. It adds the links to your working file and keeps a copy of the file as it was before. It also adds the page breaks and system breaks of the print, so that the score can be drawn with the same systems as the print.

# %%
link_work(GRIEG)

# %% [markdown]
# ## 7. Follow one link
#
# Choose a bar, then follow its link by hand in `work.mei` (reopen the file if the editor still shows the old version). Searching with Ctrl+F (on a Mac Cmd+F) is the quickest way.
#
# 1. **The bar.** Search for `<measure n="` followed by your bar number and `"`, for example `<measure n="20"`. The first bars 1 and 2 you find are in the header, in the *incipit* (the opening of the piece, as part of the description of the work); the music comes later, after `<music>`.
# 2. **Its link.** The bar has an attribute `facs`: `#` followed by the `xml:id` of a zone. Copy that `xml:id`.
# 3. **The zone.** Search for it with the quotation marks, for example `"zone-grieg-voglein-p0001-020"`. The `<zone>` has the four numbers of the box: `ulx`, `uly`, `lrx`, `lry`.
# 4. **The page.** The zone is inside a `<surface>`, the page. Its `<graphic>` names the image file, seen from the folder of `work.mei`.
#
# Write your bar number after `BAR =` and run the cell: it shows the same chain, with line numbers, and the box on the page.

# %% source-media
BAR = 20

follow_link(GRIEG, BAR)

# %% [markdown]
# ### The other way: from the page to the bar
#
# Run the next cell. It draws the score from `work.mei` and shows the page next to it. Click a bar in the score: its box lights up on the page. Click a box on the page: its bar lights up in the score. Try your bar, a half bar (9, 10, 30 or 31), and the last bar on page 42 and the first on page 43 (bars 20 and 21). The score is drawn again each time you save `work.mei`.
#
# The viewer counts like the file: "Measure 20" is bar 20. Its summary lists 41 measures, 2 of them without `facs`: these are the two bars of the incipit in the header, which are not part of the music on the pages.

# %% source-media
from camat import launch_interactive_facsimile_viewer

if "viewer" in globals():
    viewer.stop_watch()
viewer = launch_interactive_facsimile_viewer(
    str(WORK_MEI), auto_watch_mei=True, verovio_breaks="encoded",
    verovio_options={"header": "none", "footer": "none"},
)

# %% [markdown]
# ## 8. Check the file
#
# The next cell checks `work.mei` against the MEI rules (the *schema*), follows every link to its zone, checks that both page images are there, and draws the file with Verovio. It shows only problems that are new since before the links: the encoding already has a few remarks of its own, which we look at in block 2.
#
# **Checkpoint:** `work.mei` has no new problems, all 39 bars point to boxes on two pages, and both pages are reviewed.

# %%
check_links(GRIEG)

# %% [markdown]
# ## At the end
#
# Your working file `work.mei` now has the links. The next notebook, `03_grieg_repository`, puts your edition on GitHub; block 2 continues with the same file. Run the last cell to stop the pictures and the score from watching their files.

# %%
stop_watching()
viewer.stop_watch()

# %% [markdown]
# Links: the [IMSLP scan](https://imslp.org/wiki/Special:ImagefromIndex/28165), the [encoding in the MEI Sample Collection](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Grieg_Little_bird_Op43_No4.mei), [CAMAT's guide to linking a PDF](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_pdf_facsimile_guided.ipynb), and the [MEI Guidelines on facsimiles](https://music-encoding.org/guidelines/v5/content/facsimilesrecordings.html). The encoders' credits and the licence are in `grieg_edition_work/inputs`.
