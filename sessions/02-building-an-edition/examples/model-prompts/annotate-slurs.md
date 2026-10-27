Work on MEI 5.1, Schumann Op.68 No.10, edition/mei/work.mei.

Human-verified reading supplied for this exercise: IMSLP 51556, printed p.8,
first system, has a slur from pickup C3 (d1e60) to F3 (d1e338) in the first
full bar, then a separate slur from B-flat3 (d1e561) to A3 (d1e634) in the
second full bar. The upstream encoding instead joined d1e60 to C4 d1e619.
Our starter already has the F3 pitch correction; do not change notes.

Propose only an MEI <annot> child of pickup measure d1e9, after its staves and
any control events. Use xml:id="seminar-annot-opening-slurs", type="editorial",
label="Opening slur division", and plist="#d1e60 #d1e338 #d1e561 #d1e634".
Put concise prose in a <p>: identify the witness/page, explain the two slurs and
the inherited discrepancy, and state that other missing expressive marks remain
to be edited. Do not claim a complete proofread, personal source inspection,
validation, or human approval. The editor will check your words against the scan.

Return the proposed fragment and what needs human verification. Do not edit
files, run commands, add/change slurs or notes, re-export or reformat the MEI.
If the existing targets are unavailable, ask for the excerpt first. Default MEI
namespace: http://www.music-encoding.org/ns/mei.

<!-- Paste the relevant measures/IDs from the working file here. -->
