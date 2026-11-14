# %% [markdown]
# # The header and the printed marks
#
# Session 3, *Linking and editing*: block 2.
#
# In block 1 you linked every bar of Grieg's *Vöglein* to its place in the print. Now you work on the encoding itself:
#
# 1. you read its *header*, the part of the MEI file that says where the encoding comes from, and add what you know about our print and about your own work;
# 2. you restore the printed marks of one system that the encoding leaves out: dynamics, slurs and pedal marks, with the score and the print side by side;
# 3. another pair checks your marks against the print, and you check theirs.
#
# This notebook continues in the folder `grieg_edition_work` of `03_grieg_linking.ipynb` and `03_grieg_repository.ipynb`: run those first. You edit the same file, `grieg_edition_work/edition/mei/work.mei`, and after each task you record your change as a commit in your repository.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong, the message appears under the cell.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed. The second defines helper functions; it is collapsed because you do not need to read it. The third finds your working file and the file as it was before editing, which the notebook compares it with.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: grieg_linking grieg_editing

# %%
PROJECT = Path.cwd() / "grieg_edition_work"
GRIEG = open_edition(PROJECT)
WORK_MEI = GRIEG["work"]

# %% [markdown]
# ## 1. What the header is for
#
# Remember the Schumann piece of session 2: in bars 1 and 5, the encoding has an A3 in the left hand where our print has an F3. Nobody typed it wrong. The encoding was made from another source, a file from the KernScores collection, not from the Clara Schumann edition we compared it with. Its header said so, for anyone who read it.
#
# Reusing an encoding saves a lot of typing. The header tells you what you are reusing: from which source, by whom, and with which changes since. The next cell shows the header of `work.mei` in plain words, with the lines where you find each part in the file.

# %%
show_header(GRIEG)

# %% [markdown]
# Read the summary, and look up each part in `work.mei` with the line numbers:
#
# - The header names two sources. Which one is our print? Compare its plate number with the number at the bottom of page 42.
# - Read the first two changes. From which file were the notes made, and when? Does the header say that anyone compared them with the Peters print?
# - Changes 3 and 5 point to two tools, `#xsl_ppq` and `#xsl_header`, that the file does not describe. A `#` link works like `facs="#zone-…"` in block 1: it must point to an `xml:id` in the same file. These two point to nothing, and CAMAT's checker reports them as errors.

# %% [markdown]
# ## 2. Your names and your system
#
# Each pair restores the marks of one system. Write your names and the system your teacher gave you, then run the cell. The names go into the header of `work.mei`, and so into your public repository: names, initials or GitHub usernames are all fine.

# %%
NAMES = ""   # for example "Anna and Ben"
PAGE = 42    # 42 or 43
SYSTEM = 1   # 1 to 5, from the top of the page

choose_system(GRIEG, PAGE, SYSTEM)

# %% [markdown]
# ## 3. Add to the header
#
# The header does not know two things yet: exactly which scan we use, and what you did. The next cell prints the lines to add, with your names, your system and today's date, and the line numbers where they go.
#
# 1. Open `work.mei` in the editor, go to the line the cell names (Ctrl+G, then the line number), and paste the two `<identifier>` lines.
# 2. Paste the `<change>` before `</revisionDesc>`. Read it: does it say what you did? Change the words if not.
# 3. Save the file, then run the cell after next.

# %%
header_lines(GRIEG, NAMES)

# %%
check_header(GRIEG)

# %% [markdown]
# When the check shows three ✓, record your change: in VS Code's **Source Control** view of the edition folder, write the message *Add the scan and our work to the header*, click **Commit**, then **Sync Changes**. Do the same after each task below, with a message that says what you did.
#
# <details><summary>Why the fingerprint of the scan?</summary>
#
# IMSLP sometimes replaces a scan with a better one under the same file number. Our boxes would then no longer fit. With the fingerprint (SHA-256), anyone can check later that they have exactly the file we linked to: block 1 did the same check after the download.
#
# </details>
#
# **Extension: repair the two broken links.** In `<appInfo>` (in `<encodingDesc>`), after the last `</application>`, add a description of each tool. Then the check in part 5 lists the two errors as gone.
#
# ```xml
# <application xml:id="xsl_ppq">
#   <name>ppq.xsl</name>
# </application>
# <application xml:id="xsl_header">
#   <name>Header.xsl</name>
# </application>
# ```

# %% [markdown]
# ## 4. Restore the marks of your system
#
# ### 4a. Your system in the print and in the score
#
# The next cell shows your system in the print, with its bar numbers. The cell after it starts the live score from block 1: click a bar to see its box on the page. Then open `work.mei` in the editor next to the notebook.

# %% source-media
show_system(GRIEG)

# %% source-media
from camat import launch_interactive_facsimile_viewer

if "viewer" in globals():
    viewer.stop_watch()
viewer = launch_interactive_facsimile_viewer(
    str(WORK_MEI), auto_watch_mei=True, verovio_breaks="encoded",
    verovio_options={"header": "none", "footer": "none"},
)

# %% [markdown]
# Compare the print with the score. The encoding has the notes, the ties, the staccato dots and the accents. Of the marks below and between the staves it has only two: *p* in bar 1 and *pp* in bar 10. Slurs, pedal marks, fingerings, the tempo words and most dynamics are missing. You restore them for your system.
#
# ### 4b. The notes of your system
#
# A mark in MEI says where it belongs: in which bar, on which staff, and on which *beat*. The beat is the number you write in `tstamp`. In 6/8 a bar has six beats, one for each eighth note; the short 32nd notes fall between them (¼, ½, ¾). A slur instead names its first and last note by their `xml:id`.
#
# The next cell lists the notes of your system: for each bar and staff, the beat, the pitch and the `xml:id`. Short notes beamed together are on one line.

# %%
show_notes(GRIEG)

# %% [markdown]
# ### 4c. By hand: the dynamics
#
# Look for the dynamics of your system in the print: letters such as *p*, *pp*, *f* or *fz*, words such as *cresc.*, and *hairpins*, the long opening or closing wedges. Add each one inside the `<measure>` where it begins, after its two `<staff>` elements, before `</measure>`. Change the beat, the staff and the letters to what the print shows:
#
# ```xml
# <dynam xml:id="seminar-dynam-1" staff="1" place="below" tstamp="1">pp</dynam>
# <hairpin xml:id="seminar-hairpin-1" form="dim" staff="1" place="below" tstamp="2" tstamp2="0m+6"/>
# ```
#
# - `staff="1"` is the upper staff (right hand), `staff="2"` the lower one; `place` puts the mark below or above that staff.
# - A hairpin has a beginning and an end: `form="cres"` opens, `form="dim"` closes; `tstamp2="0m+6"` means "in this bar (0 bars later), on beat 6", `"1m+2"` would be beat 2 of the next bar.
# - Every new element needs its own `xml:id`: count on, `seminar-dynam-2`, `seminar-hairpin-2` and so on.
# - **System 1 of page 42** also restores the tempo words: `<tempo xml:id="seminar-tempo-1" staff="1" place="above" tstamp="1">Allegro leggiero.</tempo>` in bar 1.
#
# Save, look at the score, and run the next cell. It lists what changed since before editing.

# %%
show_changes(GRIEG)

# %% [markdown]
# Changes marked **not part of the tasks** or **outside your system** need a second look: keep them only if the print shows them and they belong to your task. Then commit and sync, for example with the message *Add the dynamics of system 3*.
#
# ### 4d. With Copilot: the slurs
#
# The slurs are the long curved lines over or under groups of notes. For a slur, the model needs to know its first and last note. The next cell writes a prompt with the bars of your system from your file.
#
# 1. Copy the prompt into Copilot's chat (View → Chat).
# 2. Replace the line that begins with `REPLACE THIS LINE` with one line per slur, for example: *from d418889e30 to d418889e221, staff 1, above*. Take the `xml:id`s from the list in 4b.
# 3. Send it, look at the change Copilot proposes, accept it, and save `work.mei`.
# 4. Look at the score: does each slur begin and end where the print has it?
#
# **Without Copilot** (in the cloud, or if Copilot does not answer), write each slur by hand, in the `<measure>` where it begins, after its `<staff>` elements. `startid` and `endid` name its first and last note, with a `#` in front of the `xml:id`:
#
# ```xml
# <slur xml:id="seminar-slur-1" staff="1" curvedir="above" startid="#d418889e30" endid="#d418889e221"/>
# ```

# %%
slur_prompt(GRIEG)

# %%
show_changes(GRIEG)

# %% [markdown]
# Read each new `<slur>` line: it names its two notes, with pitch and bar. If the model chose other notes, correct `startid` or `endid` by hand. Language models often change more than you asked for: check every line marked with ←. Then commit and sync.
#
# ### 4e. By hand: the pedal marks
#
# Under the lower staff, *Ped.* means "press the right pedal" and ✻ "release it". In MEI both are a `<pedal>` element, with `dir="down"` for *Ped.* and `dir="up"` for ✻:
#
# ```xml
# <pedal xml:id="seminar-pedal-1" staff="2" tstamp="1" dir="down"/>
# <pedal xml:id="seminar-pedal-2" staff="2" tstamp="4" dir="up"/>
# ```
#
# Give each mark the beat under which it is printed. If the ✻ is in the next bar, its `<pedal>` goes into that bar.

# %%
show_changes(GRIEG)

# %% [markdown]
# Then commit and sync.
#
# **Keep the rest as it is.** Notes, rhythms, `xml:id`s and links stay unchanged. A mark that the print has and the encoding left out is restored as an ordinary part of the transcription.
#
# **Extensions**
#
# - **Fingerings,** the small numbers over the notes: `<fing xml:id="seminar-fing-1" staff="1" tstamp="1" place="above">2</fing>`.
# - **The words *poco ritardando*** (page 43, system 5): `<dir xml:id="seminar-dir-1" staff="1" place="below" tstamp="…" tstamp2="…">poco ritardando</dir>`.
# - **The 8va line at the page turn.** The `<octave>` in bar 20 has `tstamp2="4"`: it ends on beat 4 of bar 20. Where does the dotted line end in the print? Write that place as `tstamp2`, for example `"1m+1"` for beat 1 of the next bar.

# %% [markdown]
# ## 5. Check the file
#
# The score looks right, but is the file still correct MEI, with all its links? The next cell checks `work.mei` against the MEI rules (the *schema*), follows the links, and draws the file with Verovio. It shows only what is new since before editing, and what is gone.

# %%
check_file(GRIEG)

# %% [markdown]
# ## 6. Peer review
#
# Swap with another pair: you review their system on their laptop, they review yours. The next cell shows each bar with new marks: the marks in words, and the bar in the print. On GitHub, their commits show the same changes line by line. For every mark, check against the print:
#
# - the right bar and the right beat;
# - for a slur, the right first and last note;
# - the right staff, above or below;
# - nothing changed that should not be (the lines marked ←).
#
# A file that passes the check in part 5 is a valid file, not yet a checked transcription: only the comparison with the print shows that.

# %% source-media
show_review(GRIEG)

# %% [markdown]
# Write down what you decide. The next cell writes the review sheet, with one entry for each change in the bars, into the folder `grieg_edition_work/edition/reviews/`, named after the page and the system. Open it in the editor and write your names after *Reviewed by*. Under each entry, write your decision:
#
# - **accept**: the print shows the mark, and it is in the right place;
# - **correct**: something is wrong; the pair that restored the mark fixes it in `work.mei` while you watch;
# - **unresolved**: you could not decide together. Say why, and write it under *Unresolved* at the end of the sheet.
#
# Save the sheet and run the cell again: it counts the decisions, and lists any change that is not on the sheet yet, such as a corrected mark. The sheet stays next to `work.mei` in your repository: when it is complete, commit and sync it (*Add the review sheet*), together with any corrections. Your names on it are public too: names, initials or GitHub usernames.

# %%
review_sheet(GRIEG, NAMES)

# %% [markdown]
# **Checkpoint:** every entry on the sheet has a decision.

# %% [markdown]
# ## At the end
#
# Your work is in `work.mei` and in the commits of your repository. Check in VS Code's Source Control view that nothing is left to commit or sync. The last notebook, `03_grieg_live_page`, turns the repository into a live page. Run the last cell to stop the score from watching the file.

# %%
viewer.stop_watch()
