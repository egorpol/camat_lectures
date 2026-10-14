# Historical Music Notation as Musical Information Systems

*A teaching-oriented overview for computational musicology, with potential Jupyter notebook demonstrations (topics only; no code).* 

## Core idea

Historical musical notation is not simply an early version of staff notation. Different systems encode **pitch, contour, duration, spatial relationships, instrument actions, performance instructions, or executable sequences**. Comparing them offers a way to introduce data representation, parsing, rule-based interpretation, uncertainty, and conversion between symbolic formats.

**Guiding question:** How did people represent, store, communicate, and execute musical information before computers?

## Catalogue of historical approaches

| Period | Notation / system | Computational perspective | Possible Jupyter demonstration |
|---|---|---|---|
| c. 1400 BCE | **Hurrian Hymn H6** (Ugarit) | Incomplete and contested decoding of musical instructions | Compare alternative interpretations; represent uncertainty explicitly |
| Ancient Greece | **Greek alphabetic notation** | Mapping written symbols to pitch information | Decode a passage from the *Seikilos epitaph*; vary tuning assumptions |
| 9th century onward | **Early neumes** | Melodic contour and gestures, sometimes without fixed pitch | Generate alternative pitch realizations consistent with a given contour |
| 9th century | **Daseian notation** (*Musica enchiriadis*) | Symbols and a distinctive pitch system | Reconstruct its pitch collection; visualize or generate early organum |
| Medieval period | **Guidonian hand / hexachordal solmization** | Spatial lookup interface; overlapping hexachords and mutation | Interactive hand-to-pitch mappings and solmization pathways |
| 13th–16th centuries | **Mensural notation** | Context-sensitive rules for rhythmic interpretation | Compare written note shapes, mensuration, and calculated durations |
| 15th–17th centuries | **Lute and organ tablatures** | Encoding instrument actions or positions | Convert tablature to pitches under alternative tunings |
| 16th–18th centuries | **Figured bass** | Harmonic constraints rather than fully specified voices | Produce multiple realizations of one bass-and-figures sequence |
| Historical Chinese traditions | **Guqin wenzi pu / jianzi pu** | Verbose and compressed performance-action instructions | Represent fingering/technique and compare with resulting pitches |
| 15th century onward | **Korean jeongganbo** | Music organized in a temporal grid | Translate grid subdivisions into timed events or a piano roll |
| Historical Chinese traditions | **Gongche notation** | Scale-position symbols | Explore mode, pitch mapping, and transposition |
| 19th century onward | **Numbered notation (jianpu)** | Relative scale degrees | Transpose melodies while retaining their scale-degree encoding |
| 19th century | **Hamparsum notation** (Ottoman tradition) | Symbolic representation within a modal tradition | Compare historic symbols with alternative pitch/transcription models |
| 19th century | **Shape-note notation** | Notehead shapes as solmization information | Visualize four-shape and seven-shape systems |
| 17th century onward (earlier precedents) | **Pinned barrels / cylinders** | Physical programming of musical sequences | Simulate rotation and triggering of notes |
| 19th century | **Music Braille; Abreu notation** | Tactile symbolic encodings | Compare how different cell structures encode pitch and duration |
| Late 19th–20th centuries | **Player-piano rolls** | Mechanically executable note/event instructions | Detect perforations, reconstruct onset/duration, compare with MIDI |
| 20th century | **Klavarskribo** | Keyboard-oriented spatial notation | Re-render a melody in an alternative coordinate system |
| 20th century | **Graphic and indeterminate scores** | Procedures with multiple possible outcomes | Model rule-based or stochastic realizations, e.g. Cage's *Fontana Mix* |

*Historical dates are approximate and often refer to surviving sources or the emergence of a particular notational form rather than the origin of the underlying musical practice.*

## Recommended Jupyter case studies

### 1. Daseian notation — symbols and scale structure
- Reconstruct the unusual pitch organization of *Musica enchiriadis*.
- Map notation symbols to pitches and generate basic organum.
- **Question:** How much musical structure resides in the mapping system rather than the individual symbols?

### 2. Guidonian hand — spatial interface to musical knowledge
- Link locations on a hand diagram to the medieval gamut.
- Visualize overlapping hexachords and possible mutations.
- **Question:** Can an embodied pedagogical system be modeled as a lookup table or graph?
- **Caveat:** The developed Guidonian-hand diagram should not automatically be attributed directly to Guido of Arezzo.

### 3. Mensural notation — context-dependent interpretation
- Compare imperfect/perfect values and mensuration settings.
- Examine how surrounding notes affect rhythmic interpretation.
- **Question:** What distinguishes the written symbol from its interpreted duration?

### 4. Jeongganbo — time as space
- Represent musical rhythm through a structured grid and subdivisions.
- Convert a historical-style grid into timed events, and compare with staff notation or MIDI.
- **Question:** What changes when temporal information is encoded spatially?

### 5. Player-piano rolls — executable notation
- Compare scanned rolls, perforation event tables, and MIDI representations.
- Relate hole position/length to musical onset and activation; consider roll transport speed.
- **Question:** In what sense is a piano roll a score, recording, or program?
- **Caveat:** Ordinary rolls and reproducing rolls differ in how performance expression is represented.

### 6. Graphic scores — rules, interpretation, and indeterminacy
- Use *Fontana Mix* (John Cage, 1958) as an example of operations on visual elements.
- Model how different valid configurations lead to different musical outcomes.
- **Question:** Must a notation determine one unique realization?

## Suggested four-session teaching sequence

1. **Pitch as a symbolic system:** Greek notation → Daseian notation → Guidonian hand. Concepts: lookup tables, scale models, transposition, mapping.
2. **Time as a symbolic or spatial system:** Mensural notation → Jeongganbo → piano rolls. Concepts: contextual parsing, temporal grids, event streams.
3. **Music as an instruction for action:** Tablature → guqin notation → figured bass. Concepts: action encoding, constraint solving, underdetermination.
4. **Music as a program:** Pinned cylinders → player pianos / Conlon Nancarrow → graphic scores. Concepts: execution, machine playback, generative procedures.

## Cross-cutting questions for computational musicology

| What is primarily represented? | Examples | Computational analogy |
|---|---|---|
| Absolute or relative pitch | Greek notation, jianpu | Symbol mapping and transposition |
| Spatial organization of tonal knowledge | Guidonian hand | Lookup interface / graph |
| Melodic direction | Early neumes | Relative constraints |
| Context-sensitive rhythm | Mensural notation | Rule engine / grammar |
| Rhythm as spatial subdivision | Jeongganbo | Grid-based temporal model |
| Physical playing actions | Tablature, guqin notation | Instrument-specific instruction set |
| Partial harmonic specification | Figured bass | Constraint solving |
| Mechanically executable events | Pinned cylinders, player-piano rolls | Event stream / program |
| Multiple valid outcomes | Graphic scores | Generative or stochastic system |

**Especially useful for MEI / CAMAT:** Compare (1) the *historical written representation*, (2) its *interpreted musical meaning*, and (3) a *modern interchange representation* such as MEI or MIDI. Identify which information is preserved, inferred, or lost: fingering, solmization, mensural ambiguity, tuning, temporal nuance, or mechanical controls.

## Further reading and digital resources

- [Music Encoding Initiative — MEI Guidelines](https://music-encoding.org/guidelines/v5/content/) — historical notation encoding, including mensural and neumatic contexts.
- [Stanford University Piano Roll Archive (SUPRA)](https://supra.stanford.edu/) — digitized piano rolls and associated computational datasets.
- [Six Dragons Fly Again (2024)](https://arxiv.org/abs/2408.01096) — computational work with historic Korean *jeongganbo*.
- [Umulsai (2026)](https://arxiv.org/abs/2607.24230) — text encoding and web engraving for *jeongganbo*.
- [Corpus Musicae Ottomanicae](https://www.uni-muenster.de/CMO-Edition/en/) — historical Ottoman music notation sources and editions.

## Suggested starting selection

For a compact introductory workshop, begin with **Daseian notation**, the **Guidonian hand**, **jeongganbo**, and **player-piano rolls**: four distinct representations spanning symbolic mapping, spatial pedagogy, temporal grids, and mechanical execution. Follow with **mensural notation** for a more advanced discussion of contextual interpretation.
