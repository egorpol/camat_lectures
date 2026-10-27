# From Digital Edition to Computational Music Analysis

*Von der digitalen Edition zur computergestützten Musikanalyse: Einführung in Musik-Encoding und Tools für die Notentextanalyse*
Seminar, winter semester 2026/27. Materials in English.

This site carries the content of each session together with demos that run in your browser. Every demo also comes as a Jupyter notebook, where you change the inputs and keep your work: in session 1 on [Jupyter4NFDI](setup.md), from session 2 on [your own laptop](setup-laptop.md) or, without a laptop, [in the cloud](setup.md#from-session-2-the-cloud-route).

## Sessions

| | Session | Demos |
|---|---|---|
| 1 | [Why encode music? From notation to machine-readable scores](sessions/01-why-encode-music/index.md) | player-piano roll, one melody in seven formats, binary grids, an LLM writes ABC |
| 2 | [Building an edition: the source and the notes](sessions/02-building-an-edition/index.md) | setup on your laptop, a wrong note in Schumann, OMR next to the scan, five notes in ABC, the page and its bars |

## What the course covers

1. **Encoding:** why music needs to be encoded, and how formats from ABC and kern to MusicXML and MEI differ.
2. **Digital editions:** MEI, facsimiles and editions linked to their sources.
3. **Analysis:** note tables, piano rolls, statistics and pattern search with CAMAT.

## Tools

- [Verovio](https://www.verovio.org) renders music notation in the browser and in Python.
- [Jupyter4NFDI](https://hub.nfdi-jupyter.de) runs the notebooks in the cloud: in session 1 for everyone, later for anyone without a laptop. See [Setup](setup.md).
- [mei-friend](https://mei-friend.mdw.ac.at/) edits MEI files in the browser, from session 3 on.
- [VS Code](https://code.visualstudio.com), Python and Git run the notebooks and keep your edition's history on your laptop from session 2 on: see [Setup on your laptop](setup-laptop.md).
- [CAMAT](https://camat-v2.readthedocs.io) (Computer-Assisted Music Analysis Toolbox) from session 2 on.
