# %% [markdown]
# # Where does the bird call come back?
#
# Session 4, *Publishing and analysis*, block 2.
#
# In block 1 you built a class edition of Grieg's *Vöglein*. Now go back to your pair's own edition.
# How often does the call from bar 1 come back? How closely? Can the computer tell a repeat from an
# imitation?
#
# You'll look at the score and the scan, sort a few hits, and leave with one finding on your live page.
# Run the cells from top to bottom with Shift+Enter. If a message asks you to fix something, do that
# and run the cell again.

# %% [markdown]
# ## Setup
#
# Keep this notebook next to your session-3 folder `grieg_edition_work`. Run the three cells below.
# The first installs the packages, the second sets up the tools, and the third finds your edition.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: grieg_linking grieg_editing grieg_publish grieg_analysis grieg_search

# %%
GRIEG = open_search_folder()

# %% [markdown]
# ## 1. The bird call
#
# Bar 1 is the pickup. Follow the highlighted notes through the landing note in bar 2 and find them
# on the scan. Use the numbers shown here throughout the notebook.
#
# You met the binary grid in session 1's `01_binary_grid`. It is a piano roll drawn as filled and empty
# cells. Each row is a pitch. Time moves to the right. A dark cell means that pitch is sounding.
#
# A *repeat* brings the call back with the same rhythm and intervals (the distances between pitches).
# A *transposition* moves all its pitches up or down by the same distance. A *sequence* repeats a
# shape at new pitches. Each step can keep the rhythm and the shape while changing some intervals.

# %%
show_query(GRIEG)

# %% [markdown]
# **Checkpoint:** point out the start and landing of the call in the score and on the scan.
#
# ## 2. Search at the printed pitch
#
# A *hit* is a stretch of music the search found. A score of 1.0 means all of the call's dark cells
# are filled in that stretch. The search keeps hits from 0.75 up, so at least three quarters of the
# call's cells must be filled. A semitone is one key to the next on a piano, counting black keys.
# In this search the pitch shift is zero.
#
# First run the search with CAMAT's own functions. In block 1 you met `parse_files`, `df_pitch` and
# the piano roll.
#
# - `parse_files` reads your `work.mei` into the note table `df_pitch`.
# - The piano roll shows bars 1–5. Can you see the call come back before the search finds it?
# - `prepare_binary_timeline` moves the notes so that the pickup starts at time 0.
# - `create_binary_matrix_bundle` makes two grids, one for the piece and one for the call.
#   Each column is a thirty-second note, 0.125 of a quarter note.
# - `search_binary_query` slides the call's grid along the piece and keeps the places that score
#   0.75 or more.
#
# In the table, `source_onset_QL` is where a hit starts, in quarter notes on the piano roll's time
# line. `grid_onset_QL` is the same place on the grid, which starts at the pickup, so it is 0.5
# more. `shared_cells` counts the call's dark cells that are dark there too.

# %%
from camat import display_filtered_piano_roll, parse_files
from camat.binary_query import search_binary_query
from camat.binary_roundtrip import prepare_binary_timeline
from camat.music_utils import create_binary_matrix_bundle
from IPython.display import display

PLOTTING_BACKEND = "plt"  # Use "bokeh" for an interactive plot, then run this cell again.

results = df_pitch = camat_hits = None
if GRIEG is None:
    print("Skipped. Run the setup cells above first.")
else:
    results, dfs_by_name, last_df = parse_files(
        [str(GRIEG["work"])],
        backend="none",
        display_preview_df_pitch=False,
        display_preview_df_events=False,
        include_xml_ids=True,
        quiet_native_warnings=True,
    )
if results and not results[0]["df_pitch"].empty:
    df_pitch = results[0]["df_pitch"]
    display_filtered_piano_roll(
        df_pitch,
        measure_range=(1, 5),
        results=results,
        plotting_backend=PLOTTING_BACKEND,
        show_measure_lines=True,
        colorize_voices=True,
        display_selection=False,
    )
    notes, measure_offsets, origin = prepare_binary_timeline(df_pitch, results[0]["measure_offsets"])
    # The pickup and the landing note in bar 2.
    call = notes.loc[notes["Source Global Onset"].between(-0.5, 0.5, inclusive="left")].copy()
    call["Global Onset"] = call["Source Global Onset"] + 0.5
    if call.empty:
        print("Skipped. CAMAT found no notes of the call in bars 1–2 of your work.mei.")
    else:
        piece_grid = create_binary_matrix_bundle(
            notes, measure_offsets=measure_offsets, resolution_method="manual", manual_resolution=0.125,
        )
        piece_grid.meta["source_time_origin"] = origin  # Report hits on the time line of df_pitch.
        call_grid = create_binary_matrix_bundle(call, resolution_method="manual", manual_resolution=0.125)
        result = search_binary_query(
            piece_grid, call_grid, transpositions=[0], min_score=0.75,
            top_n=None,  # Keep every hit, not only the best five.
        )
        camat_hits = result["matches"]
        print(f"CAMAT finds {len(camat_hits)} hits.")
        display(camat_hits[[
            "score", "transpose_semitones", "source_onset_QL", "grid_onset_QL", "shared_cells", "required_cells",
        ]])
elif GRIEG is not None:
    print("Skipped. CAMAT found no notes in your work.mei.")

# %% [markdown]
# CAMAT's `plot_query_heatmaps` draws the score of every place the search tried as a *heatmap*.
# Time runs to the right, on the grid's time line. Each thin column is one start position, and its
# colour is the score there: dark for 0, yellow for 1.0. The numbered circles are the hits: the
# table above counts them from 0, the circles and the next table from 1. Where else is the colour
# bright without a circle?

# %%
import matplotlib.pyplot as plt
from camat.binary_query import plot_query_heatmaps

if camat_hits is None:
    print("Skipped. Run the search cell above first.")
else:
    plot_query_heatmaps({"Search at the printed pitch": result}, 0.125, rank=None)
    plt.show()

# %% [markdown]
# The next cell runs the same search with the course's own `search`. It numbers the hits from 1,
# the highest score first, and names their bars.

# %%
PRINTED_HITS = search(GRIEG, every_pitch=False)

# %% [markdown]
# There are six hits if your notes match the source. Look at hit 2, in bars 3–4, and compare its
# highlighted notes with the call. Does the landing fall in the same place within the bar?

# %%
show_hits(GRIEG, PRINTED_HITS, [2])

# %% [markdown]
# **Checkpoint:** you can find the second hit in the score and on the scan.
#
# ## 3. Search at every pitch
#
# This time the same grid can move up and down in pitch, and the hits are numbered again. With the
# source notes you get 23 hits. When two hits would share more than two thirds of their time, even
# at different pitches, CAMAT keeps only the one with the higher score. A new hit in bars 6–7 joins
# the hits with a score of 1.0: read its pitch shift. The hits that score 0.75 fill 12 of the call's
# 16 cells. Which of those sound like the call?

# %%
HITS = search(GRIEG)

# %% [markdown]
# Here is the same search with CAMAT's own functions: `search_binary_query` gets
# `transpositions="all"` instead of `[0]`. Now the heatmap has one row for each pitch shift, in
# semitones (`st`): `+0 st` is the printed pitch. The cell sorts CAMAT's hits like the table above,
# so each circle has the same number as there. Find the circle of the hit in bars 6–7. Which row
# is it on?

# %%
every_result = None
if camat_hits is None:
    print("Skipped. Run the search cell in part 2 first.")
else:
    every_result = search_binary_query(
        piece_grid, call_grid, transpositions="all", min_score=0.75, top_n=None,
    )
    # Highest score first, then in the order of the piece, as in the table above.
    every_result["matches"] = every_result["matches"].sort_values(
        ["score", "source_onset_QL", "transpose_semitones"], ascending=[False, True, True],
    ).reset_index(drop=True)
    print(f"CAMAT finds {len(every_result['matches'])} hits.")
    plot_query_heatmaps({"Search at every pitch": every_result}, 0.125, rank=None)
    plt.show()

# %% [markdown]
# <details><summary>How can a held chord score 0.75?</summary>
#
# A cell covers as much time as a thirty-second note. A pitch that keeps sounding fills every cell
# it passes through. The grid uses the same dark cells for repeated notes and a held note of the
# same pitch. A held chord can fill 12 of the call's cells this way. The score counts the dark
# cells that line up and lets any extra notes stand.
#
# </details>
#
# **Checkpoint:** find the hit in bars 6–7 and read its score and pitch shift.
#
# ## 4. Sort your hits
#
# Replace the numbers in `MY_HITS` with the ones your instructor gives your pair. For each hit, look
# at the score and the scan. Trace the rhythm, pitch shape and landing. Decide together whether
# it is a repeat, a sequence step (one step of a sequence) or a false hit (the cells line up but
# the music is doing something else). Give one reason for each choice.

# %%
MY_HITS = [4, 10, 11]
show_hits(GRIEG, HITS, MY_HITS)

# %% [markdown]
# CAMAT's `plot_binary_query_match` lays each hit's grid next to the call's. In CAMAT's words, the
# call is the *query* and your piece is the *host*. On the left are the call's cells, moved to the
# hit's pitch. On the right is the piece around the hit, with the hit's place in a dashed box. A
# pink outline marks a cell of the call that is filled here, a red cross one that is missing. Dark
# cells in the box without an outline are extra notes. They do not lower the score.

# %%
from camat.binary_query import plot_binary_query_match

if every_result is None:
    print("Skipped. Run the CAMAT search cell in part 3 first.")
else:
    for number in MY_HITS:
        if number in range(1, len(every_result["matches"]) + 1):
            figure = plot_binary_query_match(piece_grid, every_result, rank=number - 1)
            figure.suptitle(f"Hit {number}")
            plt.show()
        else:
            print(f"! There is no hit {number}. Choose a number from 1 to {len(every_result['matches'])}.")

# %% [markdown]
# **Checkpoint:** each hit has a kind and a reason you can point to in the music.
#
# ## 5. Add a finding to your edition
#
# Choose one of your three hits. Put its number in `MY_HIT`. The cell drafts a sentence with the search
# facts. Check the sentence against the score and scan.

# %%
MY_HIT = 4
draft_finding(HITS, MY_HIT);

# %% [markdown]
# In the next cell, choose `"repeat"`, `"sequence-step"` or `"false-hit"` for `MY_CATEGORY`.
# Replace the words in `MY_SENTENCE` with one sentence of your own about what the search score
# misses. Run the cell to save the two sentences and their note links in your edition's
# `work.mei`. The cell shows what it wrote and builds a test copy of the page here.

# %%
MY_CATEGORY = ""
MY_SENTENCE = "Replace this with one sentence about what you see in the score and scan."
write_finding(GRIEG, HITS, MY_HIT, MY_CATEGORY, MY_SENTENCE);

# %% [markdown]
# When the test build succeeds, open the edition folder's **Source Control** view in VS Code.
# Use the commit message *Add our finding*, click **Commit**, then **Sync Changes**.
#
# In your GitHub repository's **Actions** tab, wait for the *Live page* run to show a green tick.
# Run the check below and follow its link. Below the score, under **Editorial notes**, click your finding.

# %%
if GRIEG is not None:
    check_repository(GRIEG)
if GRIEG is not None and (GRIEG.get("github") or {}).get("commit"):  # once GitHub shows your branch
    try:
        check_live_page(GRIEG)
    except OSError:
        print("! The live page took too long to answer. Check your connection and try again.")
    check_live_finding(GRIEG)

# %% [markdown]
# **Checkpoint:** your live page lists the finding and highlights its notes.
#
# ## 6. Wrap-up
#
# The score measures how many of the call's cells are filled. Even 1.0 leaves room for extra notes,
# and dark cells alone cannot tell you where each note starts. What decided the kind of your hit
# when you looked at the music?
#
# <details><summary>Extension: search across octaves</summary>
#
# Paste this line into a new code cell and run it.
#
# ```python
# search(GRIEG, chroma=True)
# ```
#
# All Cs now share a row, all C-sharps share a row, and so on. These 12 rows are called pitch classes.
# The search tries all 12 shifts. Which stretches turn up when octave differences disappear?
#
# </details>
