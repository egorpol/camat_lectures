# %% [markdown]
# # The page and its bars
#
# Session 2, *The source and the notes*: the check at the end of the setup, and part 6.
#
# This notebook prepares our source for the edition. It downloads the scan, copies page 8 into a PDF of its own, draws that page as an image, and lists which bars are on which system. Next session we link every bar to its place on this image.
#
# Keep `schumann-edition-inputs.zip` in the same folder as the notebook (`get_notebooks.py` puts it there). It holds our starting MEI file and the settings for this page; the scan is downloaded when you run the notebook.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong, the message appears under the cell.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed; after the setup they already are, so it finishes quickly. The second cell defines helper functions; it is collapsed because you do not need to read it. The third checks that everything is there: it prints `CAMAT: 0.2.8` and `pypdf: 6.10.0`. During the setup, you stop there.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: pdf_preparation

# %%
import importlib.metadata
from IPython.display import display, Image
from camat.pdf_facsimile import check_poppler, parse_page_layout, check_page_layout
from camat.pdf_facsimile_guided import make_page_images, describe_pages

check_poppler()
print("CAMAT:", importlib.metadata.version("camat"))
print("pypdf:", importlib.metadata.version("pypdf"))

# %% [markdown]
# ## 1. Download the scan and copy page 8
#
# Our source is [IMSLP file 51556](https://imslp.org/wiki/Special:ImagefromIndex/51556): Schumann's *Album für die Jugend* in Clara Schumann's edition (Breitkopf & Härtel), scanned by the Bavarian State Library. The PDF has 50 pages; our piece, No. 10, is on page 8.
#
# The next cell
#
# 1. unpacks our starting files into the folder `schumann_edition_work` next to this notebook;
# 2. downloads the scan (9 MB) into `schumann_edition_work/sources`, unless `02_schumann_omr.ipynb` already did, and keeps it unchanged;
# 3. copies page 8 into a one-page PDF. In that file it is page 1, but its printed page number stays 8.
#
# It also checks that the scan is exactly the file we prepared the course with, and that the copy of page 8 comes out the same as ours.
#
# <details><summary>How can a notebook tell that two files are the same?</summary>
#
# It computes a *fingerprint* (a SHA-256 hash) from every byte of the file: a code of 64 letters and digits. If a single byte differs, the code is completely different. The notebook compares the code of your download with the one we recorded.
#
# </details>

# %%
PROJECT = Path.cwd() / "schumann_edition_work"
INPUT_BUNDLE = find_schumann_pdf_inputs()
INPUTS, SETTINGS, SOURCES = load_schumann_pdf_inputs(INPUT_BUNDLE, PROJECT)
MEI_FILE = INPUTS / "starter.mei"
OUTPUT_FOLDER = PROJECT / "edition"
MEI_HASH_BEFORE = pdf_file_sha256(MEI_FILE)

ORIGINAL_PDF, PDF_FILE, PDF_RECORD = prepare_schumann_pdfs(PROJECT, SETTINGS, SOURCES)
print("Starting MEI file:", MEI_FILE)
print("The scan, unchanged:", ORIGINAL_PDF)
print("Page 8 alone:", PDF_FILE)

# %% [markdown]
# ## 2. The page as an image
#
# CAMAT draws the one-page PDF as a PNG image at 300 dpi (dots per inch): 4167 × 5617 pixels. It writes down how it made the image in `edition/pages/pages.json`. Next session we draw a box around every bar on this image, so the image must stay exactly as it is. The notebook shows it smaller; the boxes will refer to the full size. CAMAT's message asks which pages show music: we answer that in part 4.

# %% source-media
make_page_images(PDF_FILE, OUTPUT_FOLDER, download_example=False)

# %%
PAGES_JSON = OUTPUT_FOLDER / "pages/pages.json"
manifest = json.loads(PAGES_JSON.read_text())
page = manifest["pages"][0]
assert manifest["page_count"] == 1 and manifest["dpi"] == 300
assert manifest["pdf_sha256"] == PDF_RECORD["excerpt_sha256"]
assert [page["width"], page["height"]] == SETTINGS["expected_image_pixels"]
print("Image:", PAGES_JSON.parent / page["image"])
print("Size:", page["width"], "×", page["height"], "pixels at", manifest["dpi"], "dpi")

# %% source-media
display(Image(filename=str(PAGES_JSON.parent / page["image"]), width=850))

# %% [markdown]
# ## 3. Bars and systems
#
# A system is the group of staves played together, joined by a brace at the left. Our page has five systems. The print has no bar numbers; we count as musicians do: the pickup, then bar 1 for the first full bar.
#
# The MEI file numbers its bars (`n`) from the pickup, so its numbers are one higher than ours. The table also shows each bar's `xml:id`, its name in the file. Our edition covers the pickup and bars 1–8: the first two systems.

# %%
print_bar_table(MEI_FILE, SETTINGS)

# %% [markdown]
# ## 4. Describe the page for CAMAT
#
# CAMAT needs to know which bars are on which system. We write that as one line per page:
#
# `PDF page | printed page | MEI numbers per system`
#
# The PDF page is 1 (our one-page PDF), the printed page is 8. The systems are separated by commas; `1-5` means the MEI bars 1 to 5, that is the pickup and bars 1–4. Check the line against the image above, then run the cell. CAMAT checks it against the MEI file and answers with the MEI numbers. The *step 4* in its last line is CAMAT's own next step, the linking: we do that next session.

# %%
MUSIC_PAGES = """
1 | 8 | 1-5, 6-9, 10-13, 14-17, 18-21
"""

describe_pages(MUSIC_PAGES, MEI_FILE, OUTPUT_FOLDER)

# %% [markdown]
# ### Extension: what the check can see, and what it cannot
#
# CAMAT checks that every bar of the MEI file is listed once and in order. It cannot see where a system ends on the page: that is our job. The next cell tries two wrong lines, without saving them. The first leaves out the pickup and is rejected. The second starts the second system one bar too early, and is accepted.

# %%
missing_pickup = "1 | 8 | 2-5, 6-9, 10-13, 14-17, 18-21"
try:
    check_page_layout(parse_page_layout(missing_pickup, page_count=1), MEI_FILE)
except ValueError as problem:
    print("Without the pickup: rejected.", problem)
else:
    raise AssertionError("The line without the pickup was accepted.")

wrong_break = "1 | 8 | 1-4, 5-9, 10-13, 14-17, 18-21"
check_page_layout(parse_page_layout(wrong_break, page_count=1), MEI_FILE)
print("With a wrong system break: accepted. Only a look at the image shows the mistake.")

# %% [markdown]
# ## 5. Save for next session
#
# The last cell checks everything once more and saves the table of bars, systems and IDs as `edition/measure-page-map.json`. Keep the folder `schumann_edition_work` as it is: next session continues there.

# %%
rows, checkpoint = save_schumann_page_checkpoint(PROJECT, MEI_FILE, SETTINGS, PDF_RECORD, PAGES_JSON)
assert pdf_file_sha256(MEI_FILE) == MEI_HASH_BEFORE
assert pdf_file_sha256(ORIGINAL_PDF) == SOURCES["printed_witness"]["sha256"]
print("Saved:", len(rows), "bars (the pickup and bars 1–20) on", checkpoint["systems"], "systems.")
print("The scan and the starting MEI file are unchanged.")
print("Next session: a box around each bar, linked to the MEI file.")

# %% [markdown]
# Links: [CAMAT's guide to linking a PDF](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_pdf_facsimile_guided.ipynb), the [IMSLP scan](https://imslp.org/wiki/Special:ImagefromIndex/51556), and the [MEI Guidelines on facsimiles](https://music-encoding.org/guidelines/v5/content/facsimilesrecordings.html). Our starting MEI file is based on Maja Hartwig's encoding in the MEI Sample Collection; her credits and the licence are in `schumann_edition_work/inputs`.
