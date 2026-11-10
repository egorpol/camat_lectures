# %% [markdown]
# # Editing the MEI file live
#
# Session 3, *Linking and editing*: the start of the session.
#
# At the end of session 2 we saw Copilot add a slur to our Schumann file while the score was redrawn next to it. Now you do it yourself. You edit a copy of the starting file in the editor, save it, and the notebook draws the score again. First you make one edit by hand, then one with Copilot. After each edit, you check what changed and compare it with the print.
#
# Our starting file has no slurs, dynamics or tempo words: we removed them on purpose, so that you can restore them from the print.
#
# Keep this notebook in the folder `02-building-an-edition`, next to `schumann-edition-inputs.zip` (`get_notebooks.py` puts both there). It works in the same folder `schumann_edition_work` as `02_pdf_preparation.ipynb` from session 2.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong, the message appears under the cell.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed; after the setup in session 2 they already are, so it finishes quickly. The second cell defines helper functions; it is collapsed because you do not need to read it. The third makes your working copy: `schumann_edition_work/edition/mei/work.mei`. This is the file you edit today. If it is already there, the cell keeps it as it is, with your edits.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" verovio==6.3.0

# %% helpers: live_editing

# %%
PROJECT = Path.cwd() / "schumann_edition_work"
WORK_MEI, BEFORE_MEI = prepare_work_file(PROJECT)

# %% [markdown]
# <details><summary>How do I start again from the beginning?</summary>
#
# Delete `work.mei` (or rename it, to keep it), then run the cell above again. It makes a new copy from the file as it was before editing.
#
# </details>

# %% [markdown]
# ## 1. The print
#
# The next cell shows the first two systems of page 8 of our print. It uses the page image that `02_pdf_preparation.ipynb` made in session 2. Look for what our file is missing:
#
# - **Frisch und munter.** above the first bar: the tempo words;
# - **f** under the right hand at the start: the dynamic, *forte*;
# - the long curved line in the left hand, from the pickup to the end of bar 1, and a second one in bar 2: two slurs.
#
# Remember how we count: the short bar at the start is "the pickup", and bar 1 is the first full bar. The MEI file numbers the pickup as measure 1, so bar 1 is `<measure n="2">`.

# %% source-media
show_print(PROJECT)

# %% [markdown]
# ## 2. Start the live score
#
# Run the next cell. It draws the score from `work.mei`. Because **Auto-watch MEI** is switched on, it draws the score again each time you save the file. If you save and nothing changes, click **Reload score**.

# %% source-media
from camat import launch_interactive_facsimile_viewer

if "viewer" in globals():
    viewer.stop_watch()
viewer = launch_interactive_facsimile_viewer(
    str(WORK_MEI), auto_watch_mei=True,
    verovio_breaks="encoded" if "<sb" in WORK_MEI.read_text(encoding="utf-8") else "auto",
    verovio_options={"header": "none", "footer": "none"},
)

# %% [markdown]
# Now open `work.mei` in the editor, so that you see the file and the score at the same time:
#
# - **VS Code:** in the file list on the left, open `schumann_edition_work` → `edition` → `mei` and click `work.mei`. Drag its tab to the right half of the window to see it beside the notebook.
# - **JupyterLab (cloud route):** in the file browser, open `schumann_edition_work` → `edition` → `mei` and double-click `work.mei`; it opens as text. Drag its tab to the right edge of the window.

# %% [markdown]
# ## 3. An edit by hand: the opening marks
#
# 1. In `work.mei`, search for `"d1e9"` with the quotation marks (Ctrl+F, on a Mac Cmd+F). You land on `<measure n="1" xml:id="d1e9" ...>`: the pickup.
# 2. The pickup has two `<staff>` elements, one for each hand. Put the cursor at the start of the line with `</measure>` below them, and paste these two lines:
#
#    ```xml
#    <dynam xml:id="seminar-dynam-opening" staff="1" place="below" tstamp="1">f</dynam>
#    <tempo xml:id="seminar-tempo-opening" staff="1" place="above" tstamp="1">Frisch und munter.</tempo>
#    ```
#
# 3. Save the file (Ctrl+S, on a Mac Cmd+S). The score above is drawn again, with the *f* and the tempo words. Compare it with the print.
#
# <details><summary>What do the attributes mean?</summary>
#
# `staff="1"` attaches the mark to the upper staff (the right hand), `place` puts it below or above that staff, and `tstamp="1"` puts it on the first beat of the measure. `xml:id` gives the new element a name of its own, so that other parts of the edition can point at it, just as the notes have names such as `d1e60`.
#
# </details>
#
# Then run the next cell. It lists what changed in `work.mei` since before editing, in words.

# %%
show_changes(BEFORE_MEI, WORK_MEI)

# %% [markdown]
# You should see two new elements in the pickup: a `<dynam>` and a `<tempo>`.
#
# <details><summary>The score is not drawn again, or the cell shows an error</summary>
#
# Most likely a character went missing while pasting, for example a `<` or a quotation mark, and the file is no longer correct XML. The cell above tells you the line where the problem is. Undo your last change in the editor (Ctrl+Z, on a Mac Cmd+Z), save, and paste again.
#
# </details>

# %% [markdown]
# ## 4. An edit with Copilot: the slur
#
# Now let a language model make an edit: the long slur in the left hand, from the C3 of the pickup to the F3 at the end of bar 1. The next cell writes the request (a *prompt*) for you, with the two measures from your file.

# %%
print(slur_prompt(WORK_MEI))

# %% [markdown]
# 1. Open Copilot's chat in VS Code with **View → Chat** (setup, step 6). On the cloud route, or without Copilot, use any chat assistant in your browser.
# 2. Copy the prompt from the cell above into the chat and send it.
# 3. If Copilot offers to change `work.mei` directly, look at the change and accept it. If it answers with a line of XML, paste that line into the pickup measure yourself, after the `<dynam>` and `<tempo>` from part 3.
# 4. Save the file and look at the score: is the slur there, and does it look like the one in the print?
#
# Then run the next cell.

# %%
show_changes(BEFORE_MEI, WORK_MEI)

# %% [markdown]
# Read the new `<slur>` line: it names the two notes the slur connects, with their pitch and bar. They should be the C3 in the pickup and the F3 in bar 1. If the model picked other notes, correct `startid` or `endid` by hand.
#
# Language models often change more than you asked for. Lines marked **not part of the tasks** show such changes. In class, Copilot also added a `<beam>` around two chords in bar 1. Look at the print: those two chords are indeed joined by a beam, so the change is right, but nobody asked for it. For each change like this, look at the print and decide: keep it, or undo it.

# %% [markdown]
# ### Extensions
#
# - **The second slur.** The print has another slur in the left hand of bar 2. Add it by hand or with Copilot, with a new `xml:id` such as `seminar-slur-bar2`. Which notes does it connect?
# - **The second *f*.** The second system begins with *f* again (bar 5, `<measure n="6">`). Add it as in part 3, with the new `xml:id` `seminar-dynam-second-system`.
# - **Two assistants.** Give the same prompt to a second chat assistant. Do the two answers choose the same notes? Do they change anything else?

# %% [markdown]
# ## 5. Check the file
#
# The score looks right, but is the file still a correct MEI file? The next cell checks `work.mei` against the MEI rules (the *schema*) and draws it with Verovio. It also checks the file as it was before editing, and shows only what is new: the starting file already has a few remarks, for example that the pickup is shorter than a full bar.

# %%
check_file(WORK_MEI, BEFORE_MEI, PROJECT)

# %% [markdown]
# ## At the end
#
# Your edits stay in `work.mei`; we continue with this file. Run the last cell to stop the live score from watching the file.

# %%
viewer.stop_watch()
