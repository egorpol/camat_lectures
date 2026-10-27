# %% [markdown]
# # From a scan to notes: OMR
#
# Session 2, *The source and the notes*, part 4.
#
# Optical music recognition (OMR) is a program that looks at the image of a page and proposes notes. It produces a draft, not a transcription: it can miss notes, misread pitches, merge bars, and it usually drops dynamics and words. Here we compare what two OMR programs, HOMR and OeMeR, made of page 8 of our source, Schumann's *Fröhlicher Landmann*.
#
# We ran both programs before class, because each takes minutes. This notebook loads their results from `schumann-omr-recordings.zip`, which must be in the same folder as the notebook (`get_notebooks.py` puts it there). It also downloads the scan from IMSLP (9 MB), so that you can compare.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. Everyone does parts 1 to 3; parts 4 and 5 are extensions.

# %% [markdown]
# ## Setup
#
# The first cell defines helper functions; it is collapsed because you do not need to read it. The second unpacks the recorded results into the folder `schumann_omr_work` next to this notebook.

# %% helpers: omr omr_recordings omr_view

# %%
RECORDED = load_schumann_recordings()

# %% [markdown]
# ## 1. The scan
#
# The top of page 8: the first two systems, with the pickup and bars 1–8. The print has no bar numbers; we count as musicians do: the pickup, then bar 1 for the first full bar.
#
# The cell downloads the scan once and keeps it in the folder `schumann_edition_work/sources`, where `02_pdf_preparation.ipynb` finds it later.

# %% source-media
show_schumann_scan(RECORDED)

# %% [markdown]
# ## 2. HOMR's result for the same two systems
#
# We gave HOMR only this part of the page, cut out of a picture of the whole page. HOMR wrote the notes it found as MusicXML; Verovio draws them below. Verovio chooses its own line breaks, so the systems do not end where the print's do.
#
# Compare the two pictures: the notes, but also the words and signs above and below the staves.

# %%
show_omr_score(RECORDED / "homr-two-systems/rendered/page-1.svg")

# %% [markdown]
# ## 3. Bar by bar
#
# The next cell lists one bar of HOMR's result in words, for each staff. Notes that sound together are joined with `+`. Middle C is C4.
#
# 1. Look at bar 1 and bar 5 in the bass: which pitch does HOMR read at the end of each bar? Compare it with the scan.
# 2. Change `BAR` to another bar (`"pickup"`, or 1 to 8) and run the cell again.
# 3. Find one thing HOMR got wrong or left out.

# %%
BAR = 1  # "pickup", or 1 to 8
read_bar(RECORDED, BAR)

# %% [markdown]
# <details><summary>What we found</summary>
#
# - **Bars 1 and 5, bass:** HOMR reads F3 at the end of both bars, like the print. The MEI file from the MEI Sample Collection, on which our starting file is based, has A3 there. That is how we found the wrong note (part 3 on the course page).
# - **The notes are right:** every pitch and every note length in these two systems.
# - **Words and dynamics are missing:** the tempo words *Frisch und munter.* and the *f* (forte) at the start of both systems.
# - **Beams are missing:** the print joins eighth notes with beams; in HOMR's result every eighth has its own flag.
# - **Slurs are missing or in the wrong place.** HOMR missed the start of the slur over bars 3 and 4. The other mistakes come from Verovio, the program that draws HOMR's file: in bar 2, for example, the file puts the slur on the bass notes, as in the print, but Verovio draws it from the treble. A mistake can come from any program on the way, not only from the OMR.
#
# So even a good OMR result needs a comparison with the scan, note by note and sign by sign.
#
# </details>

# %% [markdown]
# ## 4. Extension: the whole page
#
# ### HOMR
#
# We also gave HOMR the whole page. It found 21 bars, the right number: the pickup and 20 bars. But in bar 2 it put the F4 of the bass into the treble chord above it, so the bass of that bar adds up to only 3½ quarter notes. And Verovio crashes when it reads this file, so there is no score to show: in bar 9 and later, HOMR joined notes to rests as if they sounded together, and Verovio cannot handle that.

# %%
summary = musicxml_summary(RECORDED / "homr-fullpage/raw.musicxml")
print("Bars HOMR found on the whole page:", summary["parts"][0]["measures"])
read_bar(RECORDED, 2, run="homr-fullpage")

# %% [markdown]
# ### OeMeR
#
# OeMeR is a second OMR program. On our computer it ran only with older versions of some of the libraries it uses; then it took about three minutes for the page. For most of the page it reads the right hand in the bass clef, so those notes come out far too low, and at first it misses the key signature (one flat). It found 19 bars instead of 21, has a rest where the print has the bass C3 of the pickup, and has no dynamics or slurs. Compare its score with the scan: a file that Verovio reads without complaint can still be full of recognition errors.

# %%
summary = musicxml_summary(RECORDED / "oemer-cpu/raw.musicxml")
print("Bars OeMeR found on the whole page:", summary["parts"][0]["measures"])
show_omr_score(RECORDED / "oemer-cpu/rendered/page-1.svg")

# %% [markdown]
# Each run has its own folder in `schumann_omr_work/recorded-…`. Its `run.log` shows what the program printed while it worked, also for two OeMeR attempts that stopped with an error before reading the page.

# %% [markdown]
# ## 5. Extension: run OMR yourself
#
# Not in class: this needs a fast internet connection, several GB of disk space, the program [uv](https://docs.astral.sh/uv/) and minutes per page. The cells below repeat what we did before class. Each switch turns on one step:
#
# - `PREPARE_NEW_INPUT` draws page 8 as an image at 300 dpi and cuts out the first two systems;
# - `INSTALL_ENGINE_ENVIRONMENTS` installs HOMR and OeMeR, each in its own Python environment, with the exact versions we used;
# - `RUN_FRESH_OMR` runs HOMR on the page and on the two systems, and OeMeR on the page;
# - `CONVERT_FRESH_OUTPUTS` converts each MusicXML result to MEI with CAMAT.
#
# Each new run goes into a new folder (`NEW`); nothing you already have is overwritten.

# %%
PREPARE_NEW_INPUT = False
INSTALL_ENGINE_ENVIRONMENTS = False
RUN_FRESH_OMR = False
CONVERT_FRESH_OUTPUTS = False

NEW = OMR_WORK / "fresh-01"  # Choose a new name for another try.
UV = shutil.which("uv")
ENGINES = ("homr", "oemer")

# %%
if PREPARE_NEW_INPUT:
    full_image, cropped_image = prepare_schumann_image(get_schumann_scan(RECORDED), NEW / "local/input")
    print(full_image, cropped_image)
else:
    print("Off. Set PREPARE_NEW_INPUT = True to draw page 8 again.")

# %%
engine_pythons = {}
for engine in ENGINES:
    venv = NEW / "environments" / engine
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    engine_pythons[engine] = python
    recorded_env = "homr-fullpage" if engine == "homr" else "oemer-cpu"
    requirements = RECORDED / recorded_env / "requirements.txt"
    commands = [
        [UV or "uv", "venv", "--python", "3.11", str(venv)],
        [UV or "uv", "pip", "install", "--python", str(python), "--no-deps", "-r", str(requirements)],
    ]
    for command in commands:
        print(subprocess.list2cmdline(command))
    if INSTALL_ENGINE_ENVIRONMENTS:
        if not UV:
            raise RuntimeError("Install uv first.")
        if venv.exists():
            raise FileExistsError(f"Keeping the existing environment: {venv}")
        for command in commands:
            subprocess.run(command, check=True)

# %%
fresh_runs = []
if RUN_FRESH_OMR:
    inputs = [("homr", "fullpage", "schumann-page.png"),
              ("homr", "two-systems", "schumann-two-systems.png"),
              ("oemer", "fullpage", "schumann-page.png")]
    for engine, scope, filename in inputs:
        if engine not in ENGINES:
            continue
        destination = NEW / "runs" / f"{engine}-{scope}"
        record = run_omr(engine, engine_pythons[engine], NEW / "local/input" / filename, destination)
        print(engine, scope, record["status"], record.get("output"))
        fresh_runs.append(destination)
else:
    print("Off. The recorded results above stay available.")

# %%
CAMAT_PYTHON = sys.executable  # The Python that has CAMAT; in the seminar environment, this one.
if CONVERT_FRESH_OUTPUTS:
    for run_folder in fresh_runs:
        raw = run_folder / "raw.musicxml"
        if raw.exists():
            print(convert_omr_to_mei(raw, run_folder / "converted", python=CAMAT_PYTHON))
else:
    print("Off. Set CONVERT_FRESH_OUTPUTS = True after a fresh run.")

# %% [markdown]
# ## Where this leads
#
# For our edition we start from an existing MEI encoding of the whole piece, not from an OMR result. We check it against the scan just as carefully: comparing it with HOMR's reading is how we found the wrong note in bars 1 and 5.
#
# Links: [HOMR](https://github.com/liebharc/homr), [OeMeR](https://github.com/BreezeWhite/oemer), [Verovio](https://www.verovio.org), [CAMAT](https://github.com/egorpol/camat_v2), the [IMSLP scan](https://imslp.org/wiki/Special:ImagefromIndex/51556), and the [MEI encoding](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei) by Maja Hartwig in the MEI Sample Collection.
