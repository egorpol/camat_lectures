# From Digital Edition to Computational Music Analysis

**Live site: <https://egorpol.github.io/camat_lectures/>**

Materials for the seminar *Von der digitalen Edition zur computergestützten
Musikanalyse: Einführung in Musik-Encoding und Tools für die
Notentextanalyse* (winter semester 2026/27). The materials are in English.

Each session has a page on the live site with the content and demos that run
in the browser. Every demo also comes as a Jupyter notebook, in which you change
the inputs and keep your work. In session 1 the notebooks run on
[Jupyter4NFDI](https://hub.nfdi-jupyter.de); from session 2 on they run on the
students' own laptops in VS Code
([setup](https://egorpol.github.io/camat_lectures/setup-laptop/)) and use
[CAMAT](https://github.com/egorpol/camat_v2), the Computer-Assisted Music
Analysis Toolbox.

## Sessions

| | Session | Demos |
|---|---|---|
| 1 | [Why encode music? From notation to machine-readable scores](https://egorpol.github.io/camat_lectures/sessions/01-why-encode-music/) | player-piano roll, one melody in seven formats, a facsimile-linked page, binary grids, an LLM writes ABC |
| 2 | [Building an edition: the source and the notes](https://egorpol.github.io/camat_lectures/sessions/02-building-an-edition/) | laptop setup, a wrong note in Schumann Op. 68 No. 10, OMR next to the scan, five notes in ABC, the page and its bars |

Sessions 2–4 build one edition of Schumann's *Fröhlicher Landmann*. All its
notebooks and data live in `sessions/02-building-an-edition/`, because they
share one working project (`schumann_edition_work`) next to the notebooks.

## Get the notebooks

In a notebook cell on Jupyter4NFDI (or any JupyterLab):

```python
import urllib.request
urllib.request.urlretrieve("https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.py", "get_notebooks.py")
%run get_notebooks.py
```

This copies the notebooks and supporting data ZIPs into `camat_lectures/`, one folder
per session, without git. Run it again after each session to get the new
ones; existing notebooks and data files are never overwritten. In a terminal
(in JupyterLab: *File → New → Terminal*), use the bash version instead:

```sh
curl -fsSLO https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.sh
bash get_notebooks.sh
```

The
[setup page](https://egorpol.github.io/camat_lectures/setup/) has the steps
from the first login.

Each Session 1 notebook starts with a cell that installs what it needs (Verovio 6.3.0,
mido, matplotlib, ipywidgets). Python 3.10 or later.

Session 2 needs the `seminar` environment from the
[laptop setup](https://egorpol.github.io/camat_lectures/setup-laptop/)
(Python 3.12, Poppler, CAMAT 0.2.8, Verovio 6.3.0, pypdf 6.10.0), or the
[cloud route](https://egorpol.github.io/camat_lectures/setup/#from-session-2-the-cloud-route)
for students without a laptop: a Jupyter4NFDI workshop whose image Repo2Docker
builds from [`binder/environment.yml`](binder/environment.yml) with the same
pins. Its notebooks
are [PDF preparation](sessions/02-building-an-edition/notebooks/02_pdf_preparation.ipynb)
(with `schumann-edition-inputs.zip`; fetches the IMSLP scan at runtime),
[OMR results](sessions/02-building-an-edition/notebooks/02_schumann_omr.ipynb)
(with `schumann-omr-recordings.zip`, recorded HOMR/OeMeR runs) and
[note entry](sessions/02-building-an-edition/notebooks/02_note_entry.ipynb).
The notebooks for sessions 3 and 4 will go into the same folder, because all
Schumann notebooks share one working folder.

## Repository layout

- `docs/`: the live site ([MkDocs Material](https://squidfunk.github.io/mkdocs-material/)); the demo code is in `docs/javascripts/`.
- `sessions/NN-slug/`: per session, the example encodings (`examples/`) and the notebooks (`notebooks/`); session 2 also has its source record (`sources/`).
- `tools/notebooks/`: the notebook sources (percent format) and their helpers. `tools/build_notebooks.py` builds the `.ipynb` files from them, so edit the sources, not the notebooks.
- `binder/environment.yml`: the environment for the cloud route (Repo2Docker reads only this folder).
- `get_notebooks.py`, `get_notebooks.sh`: the download scripts above (Python for a notebook cell, bash for a terminal; they do the same).

## Build the site

```sh
python -m venv .venv
.venv/bin/pip install mkdocs==1.6.1 mkdocs-material==9.7.7 pymdown-extensions==12.2 nbformat
.venv/bin/python tools/build_notebooks.py    # after changing tools/notebooks/
.venv/bin/mkdocs serve                       # preview at http://127.0.0.1:8000/camat_lectures/
.venv/bin/mkdocs gh-deploy                   # publish: pushes the built site to gh-pages
```

## Third-party material

Not stored in this repository; the demos and notebooks fetch these at runtime:

- MIDI files of SUPRA, the Stanford University Piano Roll Archive (roll
  `dc920rk8870`), [CC BY-NC-SA 4.0](https://github.com/pianoroll/SUPRA).
  Zhengshan Shi, Craig Stuart Sapp, Kumaran Arul, Jerry McBride and Julius O.
  Smith III, "SUPRA: Digitizing the Stanford University Piano Roll Archive",
  *ISMIR 2019*.
- Scan `bsb00023199`, image 13, from the
  [Bayerische Staatsbibliothek](https://www.digitale-sammlungen.de/en/view/bsb00023199?page=13),
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/),
  loaded from the library's IIIF server.
- [Verovio](https://www.verovio.org), loaded from jsdelivr in the browser
  and installed with pip in the notebooks.

The MEI excerpt in `sessions/01-why-encode-music/examples/facsimile/` comes
from the CAMAT corpus edition
[DdT 1, vol. 11](https://github.com/egorpol/DdT_1_vol_11) under the MIT
License (see the `LICENSE` file in that folder).

Session 2's Schumann MEI teaching derivatives credit Maja Hartwig and the
[MEI Sample Collection](https://github.com/music-encoding/sample-encodings).
They retain the encoding's public-domain statement and the collection's
[ECL-2.0 license](sessions/02-building-an-edition/examples/schumann/LICENSE).
OMR recordings are generated notation and text diagnostics; the IMSLP scan
and model weights are fetched at runtime rather than committed.

Changes are listed in [CHANGELOG.md](CHANGELOG.md).
