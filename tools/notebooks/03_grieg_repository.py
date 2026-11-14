# %% [markdown]
# # Your edition on GitHub
#
# Session 3, *Linking and editing*: the end of block 1.
#
# In `03_grieg_linking` you linked every bar of Grieg's *Vöglein* to its box on the page. Now the edition goes into a *repository*: a folder whose versions Git records, kept on GitHub, where anyone can see it. From now on every change you make becomes a recorded version with a short message. In block 2 your edits are recorded this way, and at the end of block 2 the repository becomes a live page.
#
# By the end of this notebook:
#
# - your edition folder is a public repository on GitHub;
# - you have opened your MEI file from GitHub in mei-friend, with the page and its boxes.
#
# This notebook works in the folder `grieg_edition_work` of `03_grieg_linking.ipynb`: run that notebook to the end first.
#
# **Your repository is public.** Anyone can read it, including the names you write into it: in the review of the boxes, the header and the review sheet. Use your names, your initials or your GitHub usernames, as you prefer.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. If something goes wrong, the message appears under the cell.

# %% [markdown]
# ## Setup
#
# The first cell makes sure the packages are installed. The second defines helper functions; it is collapsed because you do not need to read it. The third finds your edition folder.

# %% install
%pip install -q "camat[validation,notebooks]==0.2.8" pypdf==6.10.0 verovio==6.3.0

# %% helpers: grieg_linking grieg_publish

# %%
PROJECT = Path.cwd() / "grieg_edition_work"
GRIEG = open_repository_folder(PROJECT)

# %% [markdown]
# <details><summary>What are Git, a commit and GitHub?</summary>
#
# **Git** records versions of the files in a folder. Each version is a *commit*: a snapshot of all the files, with a message that says what changed, and who made the change and when. The folder with its history is a *repository*. Git runs on your laptop; you installed it in session 2.
#
# **GitHub** is a website that keeps copies of repositories and shows them to others. *Publishing* a repository sends it there with all its commits; later, *Sync Changes* sends the new commits.
#
# </details>
#
# ## 1. What goes into the repository
#
# The repository is the folder `grieg_edition_work/edition`: your MEI file, the two page images with the boxes of the bars, and CAMAT's records of the pages and boxes. The PDFs stay out, and so do the reports of the notebooks' checks.
#
# The next cell writes three files into the folder:
#
# - `README.md`, the description that GitHub shows on the page of your repository;
# - `LICENSE-encoding.txt`, the licence of the encoding you started from;
# - `.gitignore`, the list of folders that Git leaves out.
#
# Write your names, initials or GitHub usernames for the README, then run the cell. It ends with the full path of the folder: you need it in part 2.

# %%
NAMES = ""   # for example "Anna and Ben", "A. K. and B. M." or "annak and benm"

prepare_repository(GRIEG, NAMES)

# %% [markdown]
# Open `README.md` in the editor and read it. You can change it as you like; the cell does not overwrite it.
#
# ## 2. Publish it from VS Code
#
# 1. In VS Code, choose **File → New Window**, then **File → Open Folder…** and the folder the cell printed (its path ends with `grieg_edition_work/edition`). Confirm that you trust the folder.
# 2. Open the **Source Control** view: the icon of three dots joined by lines on the left, or Ctrl+Shift+G (on a Mac Cmd+Shift+G).
# 3. Click **Publish to GitHub**. VS Code asks for a name for the repository: write one with your initials, such as `grieg-voglein-ak-bm`, and choose **Publish to GitHub public repository**.
# 4. VS Code lists the files to include. Leave them all ticked and click **OK**. VS Code makes the first commit, with all the files, and sends it to GitHub. If it asks you to sign in to GitHub, use the account from session 2.
# 5. VS Code offers to open the repository on GitHub: do so, and look around.
#
# Then come back to this notebook (the first VS Code window) and run the next cell. It checks that GitHub has your commit, and prints two links.

# %%
check_repository(GRIEG)

# %% [markdown]
# ## 3. Your file in mei-friend
#
# [mei-friend](https://mei-friend.mdw.ac.at/) is an editor for MEI files that runs in the browser. Open the mei-friend link that the cell printed (on your first visit, close the welcome message). mei-friend loads `work.mei` from GitHub: the score on the left, page 42 with the bar boxes below it, and the file on the right.
#
# - Click a note in the score: the editor jumps to its line, with its `xml:id`.
# - Find bar 20 in the score and on the page. The boxes are the zones you made in block 1.
#
# mei-friend finds the page images because they sit next to the MEI file in your repository, at the place its `<graphic>` names. For a file opened from your laptop, it cannot load them.
#
# **Checkpoint:** your repository is on GitHub, and mei-friend shows your file with page 42.
#
# ## From now on: commit your changes
#
# In block 2 you edit `work.mei`. After each task, record it as a commit:
#
# 1. In VS Code's **Source Control** view of the edition folder, the changed files are listed. Write a short message above them, for example *Add the dynamics of system 3*.
# 2. Click **Commit**, then **Sync Changes**.
#
# On GitHub, each commit shows exactly which lines changed. In block 2 this also helps the pair that reviews your marks.
