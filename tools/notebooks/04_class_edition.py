# %% [markdown]
# # The class edition
#
# Session 4, *Publishing and analysis*: block 1.
#
# In session 3 each pair restored the printed marks of one system of Grieg's *Vöglein* and published
# the folder as a public GitHub repository. Now the class puts those systems together:
#
# 1. you read the class list (who restored which system, and which commit the instructor picked);
# 2. you fetch each pair's `work.mei` and review sheet, pinned to that commit;
# 3. you merge the picked systems into one complete *Vöglein*, the class edition, and read the coverage table;
# 4. you compare other versions of the same system against the print;
# 5. you look at one system beside the print;
# 6. you read CAMAT's note and event tables and plot pitches, note lengths and marks.
#
# You leave with a class edition file in your own session-3 folder, a coverage table that says who restored
# what, and CAMAT's two tables and the plots you made from them. Block 2 asks how often the bird call of
# bar 1 comes back.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong,
# the message appears under the cell: an expected problem (a missing repository, a pair that changed notes)
# is a message, not a traceback.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed. The second defines helper functions; it is collapsed
# because you do not need to read it. The third finds your session-3 folder `grieg_edition_work` and prepares
# the output folder `class_edition` inside it.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: grieg_linking grieg_editing grieg_analysis

# %%
GRIEG = open_class_folder()

# %% [markdown]
# ## 1. The class list
#
# The instructor hands out a class list: one row per pair, with the printed page, the system, the pair name,
# the GitHub repository, the commit, and whether this is the version picked for that system (`use=yes`).
#
# Paste the instructor's list into the cell below, replacing the reference row. A real list holds students'
# GitHub usernames, so it is never committed to the public course repository.

# %%
CLASS_LIST = """\
page,system,pair,repository,commit,use
42,1,Reference,egorpol/grieg-voglein-test,83eed567f,yes
"""
# Replace the list above with the instructor's list, then run this cell.

ROWS, PICKED = read_class_list(CLASS_LIST, GRIEG)

# %% [markdown]
# <details><summary>What each column means</summary>
#
# - **page** and **system**: the printed page (42 or 43) and the system from the top (1 to 5).
# - **pair**: a short name for the pair, for the coverage table.
# - **repository**: `OWNER/REPO` or `https://github.com/OWNER/REPO`.
# - **commit**: at least the first 7 characters of the commit the instructor pinned.
# - **use**: write `yes` for the version that goes into the class edition when several pairs restored the
#   same system. If one row is the only one for a system, that row is used even when `use` is empty.
#
# </details>

# %% [markdown]
# ## 2. Fetch
#
# The next cell downloads each pair's `mei/work.mei` and review sheet from GitHub, pinned to that commit, and
# stores them under `class_edition/fetched/`. A second run reads the cache and needs no network.

# %%
fetch_class(GRIEG, ROWS)

# %% [markdown]
# ## 3. Build the class edition
#
# The merge starts from your own `edition/checkpoints/before-editing.mei` (it already has your page links).
# For each system in order, it takes the picked pair's marks in that system's bars, checks that the notes
# still match the source encoding, and copies the marks into one file: `class_edition/class-edition.mei`.
# Marks outside a pair's own system, or other changes (ties, articulations, …), are listed and not copied.
# The coverage table says, for each system, who restored what and which systems are gaps.

# %%
COVERAGE = build_class_edition(GRIEG, ROWS, PICKED)
show_coverage(GRIEG)

# %% [markdown]
# How to read the table:
#
# - **merged**: that system's marks are in the class edition.
# - **gap: no pair**: nobody on the list restored this system; it keeps only the source's marks.
# - **several versions, none picked**: more than one row, and the instructor has not marked exactly one with
#   `use=yes`. The notebook never takes "the first in the list".
# - **not fetched** / **notes differ** / **not XML**: the file could not be used; the message above the table
#   says why.
# - **marks added / changed / removed**: that pair's changes against the source encoding in its own bars,
#   counting only the ones that reached the class edition.
# - **refused**: how many of that pair's changes the merge refused, such as a duplicate mark or a slur
#   that points to a note that is not there. The messages above the table name each one.
# - **outside** and **other_changes**: changes the merge left out on purpose.
# - **review_sheet**: how many entries have a decision (`accept`, `correct`, `unresolved`). A sheet can be
#   complete and still hold *unresolved* entries: that is not proof that the marks are right.
#
# The class edition is a selection of the piece, not yet the piece: gaps keep the source as it was, and a
# duplicate or broken mark is refused with a message.
#
# **Checkpoint:** everyone has the class edition and can say which systems came from which pair, and which
# have no marks from the class.

# %% [markdown]
# ## 4. Other versions
#
# When several pairs restored the same system, the next cell lists how each other version's marks in that
# system differ from the picked one. Compare the differences with the print: which reading do you prefer?

# %%
compare_other_versions(GRIEG)

# %% [markdown]
# ## 5. One system beside the print
#
# Pick a system that was merged. The next cell draws its bars from the class edition (with MEI bar numbers)
# and shows the same bars in the print from your own boxes. Compare one mark of each kind that the coverage
# table names for that system.

# %%
show_class_system(GRIEG, 42, 1)

# %% [markdown]
# ## 6. Statistics
#
# CAMAT reads a copy in `class_edition/for_camat/`. The copy leaves out the incipit, a short excerpt
# in the MEI header, so its marks are counted only once.
#
# `df_pitch` holds the notes. Follow a row from its MEI bar number (`Measure`) to its pitch and length.
# An onset is the time when a note starts. CAMAT counts a tied note once, where the tie starts.

# %%
from camat import (
    check_monophonic_input,
    display_duration_distribution,
    display_filtered_piano_roll,
    display_melodic_interval_distribution,
    display_onset_position_histogram,
    display_pitch_class_distributions,
    display_pitch_distribution,
    display_successive_pitch_transition_heatmaps,
    parse_files,
)
from IPython.display import display

# Re-run the plot cells and the monophony check in section 8 after switching.
PLOTTING_BACKEND = "plt"  # Use "bokeh" for interactive plots.

# %%
mei_path = class_edition_for_camat(GRIEG)
results = dfs_by_name = last_df = None
df_pitch = df_events = None

if mei_path is not None:
    results, dfs_by_name, last_df = parse_files(
        [str(mei_path)],
        backend="none",
        display_preview_df_pitch=False,
        display_preview_df_events=False,
        include_xml_ids=True,
        parse_enharmonic=True,
        quiet_native_warnings=True,
    )
    if results:
        df_pitch = results[0]["df_pitch"]
        df_events = results[0]["df_events"]
        print(f"df_pitch has {len(df_pitch)} notes. df_events has {len(df_events)} events.")
        display(df_pitch.head(8))
    else:
        print("Skipped. CAMAT did not return tables.")

# %% [markdown]
# ### The event table
#
# `df_events` holds rests, barlines, clefs, ties, staccato dots and the marks the class restored.
# Both tables record the MEI bar, onset, staff (`Voice`) and MEI identifier (`xml_id`).
# Count the kinds of events. Then use the slur in bar 2 to see how an event points to notes.

# %%
if df_events is None or df_events.empty:
    print("Skipped. Read the class edition into CAMAT first.")
else:
    display(df_events["type"].value_counts())
    bar_2 = df_events.loc[df_events["Measure"] == 2]
    display(bar_2[["type", "subtype", "Measure", "Local Onset", "Voice", "text",
                   "start_xml_id", "end_xml_id"]])
    slurs = bar_2.loc[bar_2["type"] == "slur"]
    if not slurs.empty:
        slur_note_ids = slurs[["start_xml_id", "end_xml_id"]].stack()
        print("Notes at the ends of the slur in MEI bar 2")
        display(df_pitch.loc[df_pitch["xml_id"].isin(slur_note_ids),
                             ["xml_id", "Measure", "Local Onset", "Voice", "Pitch"]])
    else:
        print("There is no slur in MEI bar 2 of this edition.")

# %% [markdown]
# ### Notes per bar
#
# How many notes does each bar hold? Where are the highest and the lowest note?
# Count the rows of `df_pitch` with pandas. This plot always uses matplotlib.

# %%
import matplotlib.pyplot as plt

if df_pitch is None or df_pitch.empty:
    print("Skipped. Read the class edition into CAMAT first.")
else:
    notes_per_bar = df_pitch.groupby("Measure").size()
    ax = notes_per_bar.plot.bar(backend="matplotlib", figsize=(10, 3.5),
                                xlabel="MEI bar", ylabel="Notes", rot=0)
    plt.show()
    plt.close(ax.figure)
    high = df_pitch.loc[df_pitch["MIDI"].idxmax()]
    low = df_pitch.loc[df_pitch["MIDI"].idxmin()]
    print(f"Highest note is {high['Pitch']} in MEI bar {int(high['Measure'])}. "
          f"Lowest is {low['Pitch']} in MEI bar {int(low['Measure'])}.")

# %% [markdown]
# ### Piano roll
#
# Each note is a strip at its pitch. The strip is as long as the note lasts.
# Where does the music sit on the keyboard over time?

# %%
SHOW_MEASURE_LINES = True
COLORIZE_VOICES = True

if df_pitch is None or df_pitch.empty:
    print("Skipped. Read the class edition into CAMAT first.")
else:
    display_filtered_piano_roll(
        df_pitch,
        measure_range=None,
        voice_query=None,
        results=results,
        plotting_backend=PLOTTING_BACKEND,
        show_measure_lines=SHOW_MEASURE_LINES,
        colorize_voices=COLORIZE_VOICES,
        display_selection=False,
    )

# %% [markdown]
# ### A shorter selection
#
# Start with the upper staff in MEI bars 1–4 (page 42, system 1).
# The next plots compare this selection with the whole piece.

# %%
MEASURE_RANGE = (1, 4)  # Includes both MEI bar numbers. Use None for all bars.
VOICE_QUERY = ["P1 - Voice 1"]  # Upper staff. The lower staff is "P2 - Voice 1".

selection = analysis_sources = analysis_labels = selection_mono = None
if df_pitch is None or df_pitch.empty:
    print("Skipped. Read the class edition into CAMAT first.")
else:
    # Check the chosen bars and exact staff names before asking CAMAT to plot.
    matching_notes = df_pitch
    if MEASURE_RANGE is not None:
        matching_notes = matching_notes.loc[matching_notes["Measure"].between(*MEASURE_RANGE)]
    if VOICE_QUERY is not None:
        matching_notes = matching_notes.loc[matching_notes["Voice"].isin(VOICE_QUERY)]
    if matching_notes.empty:
        print("Skipped. No notes match those bars and staves.")
    else:
        selection = display_filtered_piano_roll(
            df_pitch,
            measure_range=MEASURE_RANGE,
            voice_query=VOICE_QUERY,
            results=results,
            plotting_backend=PLOTTING_BACKEND,
            show_measure_lines=True,
            colorize_voices=True,
            display_selection=True,
            display_mode="head",
            display_max_rows=10,
        )
        analysis_sources = (selection, df_pitch)
        analysis_labels = ["selection", "whole piece"]
        print(f"Selection has {len(selection)} notes.")

# %% [markdown]
# ### Pitch
#
# Which pitches come most often? The default uses the note names as written in the score.
# Each table shows counts and shares, so you can compare the two even though they have different lengths.

# %%
PITCH_X_AXIS = "pitch enharmonic"  # "midi" | "pitch real" | "pitch enharmonic"
ORDER_X_AXIS_BY = "midi"  # Low to high.
PITCH_NORMALIZE = True  # Show each count as a share of the notes in its table.

if analysis_sources is None:
    print("Skipped. Choose a selection with notes first.")
    pitch_counts = None
else:
    pitch_counts = display_pitch_distribution(
        analysis_sources,
        source_labels=analysis_labels,
        pitch_axis=PITCH_X_AXIS,
        order_axis_by=ORDER_X_AXIS_BY,
        backend=PLOTTING_BACKEND,
        plot_width=1000,
        plot_height=350,
        show_hover=True,
        show_table=True,
        normalize=PITCH_NORMALIZE,
        float_format=".3f",
    )

# %% [markdown]
# ### Note length
#
# Which note lengths come most often? `Duration` gives the length of the first note in a tie.
# `Logical Duration` joins the tied notes and gives their total length.

# %%
DURATION_COLUMN = "Duration"  # "Duration" | "Logical Duration"
DURATION_NORMALIZE = True

if analysis_sources is None:
    print("Skipped. Choose a selection with notes first.")
    duration_counts = None
else:
    duration_counts = display_duration_distribution(
        analysis_sources,
        source_labels=analysis_labels,
        duration_column=DURATION_COLUMN,
        drop_zero=True,
        round_decimals=4,
        backend=PLOTTING_BACKEND,
        plot_width=1000,
        plot_height=350,
        show_hover=True,
        show_table=True,
        normalize=DURATION_NORMALIZE,
        float_format=".3f",
    )

# %% [markdown]
# ### Pitch class
#
# A pitch class groups notes across octaves. For example, all the Cs count together.
# Compare the two plots. In the first, C♯ and D♭ share a count. In the second, each spelling has its own count.

# %%
PC_NORMALIZE = True

if analysis_sources is None:
    print("Skipped. Choose a selection with notes first.")
    pc_results = None
else:
    pc_results = display_pitch_class_distributions(
        analysis_sources,
        source_labels=analysis_labels,
        pitch_axis=PITCH_X_AXIS,
        order_axis_by=ORDER_X_AXIS_BY,
        backend=PLOTTING_BACKEND,
        plot_width=1000,
        plot_height=350,
        show_hover=True,
        show_table=True,
        normalize=PC_NORMALIZE,
        float_format=".3f",
    )

# %% [markdown]
# ### Marks per bar
#
# How many marks sit in each MEI bar? Staccato dots and accents are not counted here.
# Shaded bars belong to systems the class did not merge. This plot always uses matplotlib.

# %%
plot_marks_per_bar(GRIEG, df_events);

# %% [markdown]
# ## 7. Reading the numbers
#
# The plots count what is in the class edition file. A gap in the coverage table means those bars still have
# only the source's marks (*p* in bar 1, *pp* in bar 10, the staccato dots and accents, the 8va in bar 20).
# A merged system adds what that pair restored. The numbers are only as complete as the coverage.
#
# **Question for block 2.** The bird call of bar 1 — the short figure high in both staves — comes back later
# in the piece. How often? How exactly (the same pitches, the same rhythm, transposed)? And can the computer
# tell a repeat from an imitation?

# %% [markdown]
# ## 8. If you have time, follow one melodic line
#
# Which notes follow each other? To give a clear answer, CAMAT checks for one note at a time on each staff.
# That is what `check_monophonic_input` means here.

# %%
selection_mono = None
if df_pitch is None or df_pitch.empty:
    print("Skipped. Read the class edition into CAMAT first.")
else:
    for label, notes in (("The whole piece", df_pitch), ("The selection", selection)):
        if notes is None or notes.empty:
            print(f"Skipped. {label} has no notes.")
            continue
        mono = check_monophonic_input(notes, label=label, by_voice=True)
        if notes is selection:
            selection_mono = mono
        if mono["is_monophonic"]:
            print(f"{label} has one line per staff, so transitions and intervals can run.")
        else:
            print(f"{label} has chords, with up to {mono['max_polyphony']} notes at once on one staff.")

# %% [markdown]
# ### Which pitch comes next?
#
# Each row is a pitch. Each column is the pitch that follows it. Darker squares show pairs that come up
# more often.

# %%
TRANSITION_NORMALIZE = "count"  # "count" | "row" | "column" | "all"

if selection_mono is None or not selection_mono["is_monophonic"]:
    print("Skipped. Run the check on a selection with one line per staff.")
    transition_result = None
else:
    transition_result = display_successive_pitch_transition_heatmaps(
        selection,
        source_labels=["selection"],
        backend=PLOTTING_BACKEND,
        normalize=TRANSITION_NORMALIZE,
        by_voice=True,
        require_monophonic=True,
        plot_width=1000,
        plot_height_pitch=600,
        plot_height_pc=400,
        show_hover=True,
        show_table=True,
        float_format=".3f",
    )

# %% [markdown]
# ### How far does the melody move?
#
# An interval is the distance from one pitch to the next. A plus sign means the melody goes up.
# A minus sign means it goes down.

# %%
INTERVAL_NORMALIZE = True

if selection_mono is None or not selection_mono["is_monophonic"]:
    print("Skipped. Run the check on a selection with one line per staff.")
    interval_counts = None
else:
    interval_counts = display_melodic_interval_distribution(
        selection,
        source_labels=["selection"],
        by_voice=True,
        require_monophonic=True,
        normalize=INTERVAL_NORMALIZE,
        backend=PLOTTING_BACKEND,
        plot_width=1000,
        plot_height=350,
        show_hover=True,
        show_table=True,
        float_format=".3f",
    )

# %% [markdown]
# ### Where do notes start in the bar?
#
# The plot groups note starts into bins a thirty-second note wide (0.125 quarter-note lengths).
# For the whole piece CAMAT warns that some positions are counted together: a few notes are sixty-fourth notes,
# so they start less than a bin apart.

# %%
ONSET_BIN_SIZE = 0.125  # In quarter-note lengths.
ONSET_NORMALIZE = True

if analysis_sources is None:
    print("Skipped. Choose a selection with notes first.")
    onset_position_counts = None
else:
    onset_position_counts = display_onset_position_histogram(
        analysis_sources,
        source_labels=analysis_labels,
        dfs_by_name=dfs_by_name,
        results=results,
        selection=selection,
        full_df=df_pitch,
        bin_size=ONSET_BIN_SIZE,
        normalize=ONSET_NORMALIZE,
        edge_measure_mode="merge_to_regular",
        use_measure_metadata=True,
        backend=PLOTTING_BACKEND,
        plot_width=1000,
        plot_height=350,
        show_hover=True,
        show_table=True,
        show_measure_debug=False,
        float_format=".3f",
    )
