# %% [markdown]
# # Your edition as a live page
#
# Session 3, *Linking and editing*: the end of block 2.
#
# Your repository holds the edition as files. A *live page* shows it as a website: the score drawn by Verovio with the systems of the print, and the page image beside it, with a box for every bar. GitHub builds the page with CAMAT's site builder each time a commit arrives, and publishes it with *GitHub Pages*. After each Sync Changes, the page follows within a minute or two.
#
# By the end of this notebook your edition is online, at an address of the form `https://your-account.github.io/your-repository/`, and every bar has a link of its own.
#
# This notebook works in the folder `grieg_edition_work`, after `03_grieg_repository` and `03_grieg_editing`.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong, the message appears under the cell.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed. The second defines helper functions; it is collapsed because you do not need to read it. The third finds your edition folder and checks that GitHub has your last commit.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: grieg_linking grieg_publish

# %%
PROJECT = Path.cwd() / "grieg_edition_work"
GRIEG = open_repository_folder(PROJECT)
check_repository(GRIEG)

# %% [markdown]
# If the cell says that something is not committed or not synced yet, do that first: in VS Code's Source Control view, **Commit**, then **Sync Changes**, and run the cell again.
#
# ## 1. Two files for the page
#
# - `site.json` says what the page shows: its title, your MEI file and the page images.
# - `.github/workflows/live-page.yml` tells GitHub what to do with each new commit: install CAMAT, build the page, publish it.
#
# The next cell writes both into the edition folder, and builds a test copy of the page here, so that a problem shows up now and not on GitHub. Write the names for the page's subtitle as in the README: names, initials or GitHub usernames.

# %%
NAMES = ""   # for example "Anna and Ben"

write_live_page(GRIEG, names=NAMES)

# %% [markdown]
# <details><summary>What does the workflow file say?</summary>
#
# Open `.github/workflows/live-page.yml`. `on: push` means: run each time commits arrive. The job `build` runs on a computer of GitHub's: it gets a copy of your repository (`checkout`), installs Python and CAMAT 0.2.8, and runs `camat-build-site site.json _site`, the command that makes the page into the folder `_site`. The job `deploy` then publishes that folder with GitHub Pages. You can follow each run on GitHub, in the **Actions** tab of your repository.
#
# </details>
#
# ## 2. Switch on GitHub Pages
#
# 1. On GitHub, open your repository, then **Settings** (at the top) and **Pages** (in the list on the left).
# 2. Under **Build and deployment → Source**, choose **GitHub Actions**.
#
# Do this before the next step: GitHub publishes the page only when Pages is switched on.
#
# ## 3. Commit and sync
#
# In VS Code's **Source Control** view of the edition folder, the two new files are listed. Write the message *Add the live page*, click **Commit**, then **Sync Changes**.
#
# On GitHub, the **Actions** tab now shows a run called *Live page*: a yellow dot while it runs, about a minute, then a green tick. Run the next cell when the tick is there.

# %%
check_live_page(GRIEG)

# %% [markdown]
# ## 4. Look at your page
#
# Open the address the cell printed.
#
# - Point at a note in the score: its bar lights up on the page, and the bar number and the note's `xml:id` appear at the top.
# - Click it: the address in the browser now ends with `#voglein/` and the bar number. That is a link to this bar; send one of your bars to another pair.
# - Go to the bars of your system: are your restored marks there, as in the print?
#
# Every later commit updates the page. A correction from the peer review, for example: change `work.mei`, commit, sync, and reload the page after a minute or two.
#
# **Checkpoint:** your live page shows the score and the print, with the marks you restored.
