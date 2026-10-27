# Git and GitHub: six minutes for an editorial project

Shortened and reorganised from the
[HfM Weimar Git/GitHub introduction for editorial work](https://analyse.hfm-weimar.de/doku.php?id=en:git),
checked 26 October 2026. This adaptation is **CC BY-SA 4.0**, as is the source
wiki unless otherwise stated. Changes: compressed scope, Schumann examples,
VS Code steps, and a separate distinction between release and viewer deployment.
Use the original for installation, branches, conflicts and collaboration.

## What students need today

**Git** keeps the history of a project folder on your computer. **GitHub** hosts
a shared copy and tools for discussion/review. A **repository** is that project
with its history. A **commit** records a chosen set of changes with a message.
Saving your MEI file, committing it, and sending the commit to GitHub are three
separate actions.

Our example: we restore two printed slurs. The **diff** shows the exact XML
additions; the commit explains their purpose. The printed witness remains the
evidence for the reading. Git records the decision and who recorded it.

## The six-minute demonstration, 65–71

**65–66 — Show the repository.** Open its README, `mei/work.mei` and History.
Explain local folder versus GitHub copy. The instructor has already prepared
the repository, Git identity, login and remote; installation is not part of
this six-minute segment.

**66–68 — Show a diff.** In VS Code, open **Source Control** and select the MEI
under Changes. Read the added slurs and their endpoint IDs. Click **+** beside
only the files belonging to this editorial step: this is **staging**, choosing
what the next commit contains. Use an account-free local repository if needed.

**68–69 — Commit.** Enter a meaningful message, such as
`Restore the two opening slur phrases from IMSLP 51556`, then choose **Commit**.
The snapshot is local. Show it in the history. Students need one small commit,
not a new branch or a merge exercise today.

**69–70 — Push.** With a preconfigured remote, use **Push** from Source Control's
More Actions menu. Open GitHub and find the same commit. **Pull** brings remote
changes into the local branch; do that before a new work session with a clean
working tree. In pairs, one operator performs this step while the other reviews.

**70–71 — Distinguish the outputs.** A **tag** names a chosen commit, for example
`v0.1.0`. A GitHub **release** adds a description/downloads to that version.
**GitHub Pages** serves the built edition viewer. Creating a repository or a
release does not itself build and publish that viewer; the supplied Actions
workflow does that when enabled.

## A small command reference

For students who prefer a terminal, inside the prepared repository:

```sh
git status
git diff -- mei/work.mei
git add mei/work.mei review.json
git diff --cached
git commit -m "Restore the two opening slur phrases from IMSLP 51556"
git push
```

Stage `review.json` only after updating it. Without a configured remote, stop
after the local commit. For a new session, with no unsaved/uncommitted changes:

```sh
git pull --ff-only
```

If Git reports a conflict or the push is rejected, keep the work and ask the
instructor to inspect the histories. A shared classroom repository does not
need force pushes. A ZIP download gives files but not a working Git history;
clone the prepared repository when practising Git.

## One question to check understanding

“You saved the MEI and committed it. Can your partner already see the change
on GitHub?” **Only after the commit has been pushed.** Then check the separate
Pages deployment before promising that the public viewer has changed.

Account-free fallback: inspect the diff and commit locally; the instructor
demonstrates pushing and publication. GitHub Desktop is another graphical
interface for the same concepts. Setup details and the longer glossary remain
in the original tutorial. Official references:
[Git setup](https://docs.github.com/en/get-started/git-basics/set-up-git),
[releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository),
[Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
