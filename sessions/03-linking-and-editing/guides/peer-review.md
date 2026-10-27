# Peer review: check a reading, its encoding and its display

Block 2, **50–65 minutes**. Swap editor/reviewer roles. Use the current MEI,
the linked pre-edit checkpoint, the source scan and the saved diff/model
proposal. Use [02_review_and_release.ipynb](../../02-building-an-edition/notebooks/02_review_and_release.ipynb)
to run validation and create a blank review record. A script cannot fill in
the source-review decision for you.

## 50–53: identify the version and scope

Write the file's SHA-256 and the passage you actually inspect. MEI label 1 is
the pickup; labels 2–9 are the first eight full bars. The full 21-measure file
is the technical carrier. A successful review of three tasks is not a complete
proofread of every note and expressive mark in those nine measures.

## 53–59: compare three layers

For each task, record **accept**, **correct**, or **unresolved**, with a reason:

- **Source reading:** does the printed witness show the marking/wording and
  its extent? Consult the full system when a measure crop truncates a slur.
- **Encoding:** does the MEI attach it to the correct staff, time or exact
  start/end IDs? Is it ordinary transcription, an editorial addition or an
  uncertainty that needs explaining?
- **Engraving:** does the rendering show the intended attachment and placement?
  If the MEI is right but the renderer behaves differently, document that
  distinction rather than changing the musical reading to improve the picture.

Check that notes, rhythms, existing IDs, header credits and facsimile links
were preserved. The starter already corrects `d1e338` and `d1e1495` to F3;
do not restore the inherited A3 by accident. An LLM's explanation is a proposal
to inspect, not evidence that the source was checked by a person.

## 59–62: read the actual technical checks

Run the notebook validator, or from the edition project:

```sh
camat-validate-mei edition/mei/work.mei --output-dir edition/validation-review --verovio
```

Inspect XML/references, MEI 5.1 RELAX NG, Schematron, image resources, unchanged
input hashes and Verovio separately. Unavailable/skipped required checks are
incomplete. The optional CAMAT parse consumer is not requested here. Known
rhythm advisories include the short pickup and inherited lower-staff layers
outside this exercise; inspect them without inventing notes/rests to silence
the report.

## 62–65: record and checkpoint

Fill in the generated `edition/review.json`: reviewer, exact file hash,
reviewed labels, individual decisions, unresolved issues and validation report.
Set source review to `reviewed` only after the person named performed it.
Leave it `not_reviewed` if demonstrating the pipeline with prepared fragments.

If an accepted change needs correction, edit, rerender/revalidate, then update
the review to the new file hash. Keep the earlier candidate/proposal separately.
An altered file with an old review hash needs a fresh check. Preserve a
checkpoint inside `edition/mei/` so its relative image paths still resolve.

The next publication step exports a copy, keeps the working MEI intact and
carries the review record and declared limitations into the release project.
