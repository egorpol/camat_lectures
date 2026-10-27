# Schumann — three editorial tasks

Prepared 24 October 2026. This is an AI-assisted teaching draft for instructor
review. The [exercise solution](exercise-solution.mei) answers the three tasks;
it does **not** restore every expressive marking in the first eight bars or
claim that the remainder of the piece is edited. All 21 measure elements
remain as the technical carrier for the one-page facsimile.

## Files and the distinction between stages

- [Technical baseline](baseline.mei): inherited musical text, with explicit
  five-line staves and 20 slurs relocated to the measures of their starts.
  These relocations preserve endpoints; those endpoints are not thereby
  approved against the print. A broken historical stylesheet reference is
  preserved as text instead of an unresolved link.
- [Student starter](../../examples/schumann/starter.mei): baseline with all
  body slurs, dynamics, tempo, verbal directions and articulations deliberately
  omitted. The omission log records **22 slurs, 3 dynamics, 1 tempo, 1 direction
  and 20 articulations**. Except for the two source-based A3 → F3 corrections (`d1e338`, `d1e1495`), musical note/rhythm/voice structure and existing IDs
  are unchanged.
- [Exercise solution](exercise-solution.mei): the starter plus the five control
  events below and one editorial annotation. It remains an incomplete teaching
  edition.
- [Manual-entry scaffold](../../examples/schumann/manual-entry.mei) and
  [manual-entry solution](manual-entry-solution.mei): pickup and first full bar
  only. Students replace invisible duration placeholders with the actual music.

The upstream credits, rights statement, bibliography and revision history are
retained. The duplicate header incipit is omitted in all derivatives so that
students work with one encoded score. A new edition statement, witness record,
project description, preparation-script credit and dated revision explain the
derivative. See the [source record](../../sources/README.md),
[upstream license](../../examples/schumann/LICENSE) and [changes.json](changes.json).

## Task 1 — opening tempo and dynamic

Location: MEI label **1**, pickup, measure ID `d1e9`. The printed wording is
“Frisch und munter.”, including its final full stop. The initial dynamic is
`f`. Insert the following as children of the measure,
after the staves, rather than inside a note layer:

```xml
<dynam xml:id="seminar-dynam-opening" staff="1" place="below" tstamp="1">f</dynam>
<tempo xml:id="seminar-tempo-opening" staff="1" place="above" tstamp="1">Frisch und munter.</tempo>
```

The pickup is a short measure (`metcon="false"`); `tstamp="1"` anchors the
instruction at its first event. The base encoding used `tstamp="0.5"` for the
tempo, which is not copied into the model answer. This timing normalization
affects a control event, not the duration or pitch of a note.

## Task 2 — forte at the second printed system

Location: musical bar **5**, MEI label **6**, measure ID `d1e1231`.
The source shows `f`; the original sample omits it entirely at this location.
This task therefore restores a source sign, not just a deliberately deleted
element. Insert after the staves in label 6:

```xml
<dynam xml:id="seminar-dynam-second-system" staff="1" place="below" tstamp="1">f</dynam>
```

Check it against the first lower-staff note of that printed system. Until the
source breaks are written in the facsimile step, Verovio's automatic systems
need not match the printed systems; find the measure by its label/ID.

## Task 3 — opening slur division and explanation

The print separates the pickup/first-full-bar phrase from the next bar:

1. Pickup C3, `d1e60`, to the final F3 of the first full bar, `d1e338`.
   Store this slur in MEI label **1**, where it starts.
2. B-flat3, `d1e561`, to the final A3 of the second full bar, `d1e634`.
   Store this slur in MEI label **3**.

```xml
<!-- In measure n="1": -->
<slur xml:id="seminar-slur-pickup" staff="2" curvedir="above"
      startid="#d1e60" endid="#d1e338"/>

<!-- In measure n="3": -->
<slur xml:id="seminar-slur-bar2" staff="2" curvedir="above"
      startid="#d1e561" endid="#d1e634"/>
```

The first slur in the original MEI instead points from the pickup to C4
`d1e619` in label 3. Do not mistake that inherited reading for evidence of
what this print says. The model deliberately follows the selected witness.

The solution adds this annotation in label 1:

```xml
<annot xml:id="seminar-annot-opening-slurs" type="editorial"
       label="Opening slur division"
       plist="#d1e60 #d1e338 #d1e561 #d1e634">
  <p>IMSLP 51556, printed p. 8, first system: the pickup-to-F3 slur
  ends in the first full bar; a separate B-flat3-to-A3 slur occupies
  the second full bar. The base MEI instead joins the pickup to C4
  in the second full bar. This exercise follows the selected print.
  Other missing expressive marks remain to be edited.</p>
</annot>
```

Different prose is fine if it identifies evidence, targets and the decision.
Use ordinary transcription for the two printed slurs. `<supplied>` would be
appropriate for an editorial addition absent from the witness, not for a mark
absent only from this starter. MEI documents [slur anchors](https://music-encoding.org/guidelines/v5/elements/slur.html)
and [annotations](https://music-encoding.org/guidelines/v5/elements/annot.html).

## Manual-entry check

The pickup contains an eighth rest on staff 1 and C3 eighth on staff 2.
In the first full bar, the lower-staff melody is F3 dotted quarter, A3 eighth,
C4 dotted quarter, F3 eighth. The upper staff has eighth rest; C4–F4–A4 eighth
chord twice; two eighth rests; F4–A4–C5 eighth chord twice; eighth rest.
Each full-bar layer totals four quarter-note units. Preserve the existing
measure IDs and give newly entered notes/chords distinct IDs.

## Checks and limits

All five derivatives pass the executed XML/reference, RELAX NG, Schematron,
resource and unchanged-input checks. Verovio loading/rendering also passes.
The [validation record](validation/run.json) retains the exact code, schema,
dependency and input identities; [findings](validation/findings.json) retains
the rhythm warnings. The CAMAT parse consumer was not run.

Expected diagnostics: short pickup layers in label 1. The full-piece files
also inherit three-quarter-note second layers in the lower staff at labels
15 and 21; these remain flagged for later review, outside the core passage.
No rests or notes were invented to silence those reports. The image-network
check was not requested; the files have no facsimile yet.

The validator was run from CAMAT checkout `8774ad2ef7be9b5d0d98e82de87a85b4fdd69b13`.
That environment's installed distribution metadata reports an older version;
the record identifies the actual checkout and source hashes. This is not a
clean-install rehearsal of the student environment.

[Starter preview](previews/starter.png), [solution preview](previews/exercise-solution.png),
and [manual-entry preview](previews/manual-entry.png) were rendered with Verovio
6.3.0 and visually inspected. Their layout is automatic; printed breaks and
facsimile links belong to the next step. The annotation's prose is displayed
by the viewer's editorial panel, rather than engraved into the score image.

To regenerate the templates from the unchanged local source, run
`python tools/prepare_schumann_starter.py` from the repository root with lxml
installed. Do not run this on a student's working copy.

## Pitch correction found during the OMR comparison

The earlier preliminary source check missed two discrepancies. IMSLP 51556, printed p. 8, has F3 as the final bass eighth in the first full bar of both the first and second systems (MEI labels 2 and 6). The reused MEI has A3 at `d1e338` and `d1e1495`. The starter and teaching solutions now use F3; the upstream file and technical baseline retain A3. See `changes.json`. The initial check was not a complete note-level verification of labels 1–9. Further comparison remains necessary.
