# mei-friend: a second editing interface

Block 2, **40–50 minutes**. Use a disposable copy of `edition/mei/work.mei` in
[mei-friend](https://mei-friend.mdw.ac.at/). No GitHub login is needed for local
open/save. Keep the notebook/source visible alongside it if local image paths
do not resolve in the hosted application.

## A ten-minute demonstration

1. **40–42:** File → Open file; choose the copied MEI. Open ordinary MEI, then
   select the pickup note and connect notation selection with `d1e60` in code.
2. **42–45:** use the code search or notation to locate the editorial annotation.
   Show its anchors and edit one phrase of the explanation. Keep notes and IDs.
   The task is to compare editing interfaces, not repeat all three restorations.
3. **45–47:** Code → Validate, and inspect the feedback. Show the facsimile
   panel when images are available. As an alternative to rehearse before class,
   use the application's documented Beethoven example with web images; label
   the repertoire switch explicitly.
4. **47–50:** File → **Save MEI**, saving a new file. Reopen it and compare it
   with the imported copy. Use normal MEI, not MEI Basic or a Verovio re-export,
   for this round trip. Check existing IDs, annotation targets and facsimile
   links before promoting any saved result to the canonical working file.

Menu labels were checked against the current application/documentation on
26 October 2026. The [cheat sheet](https://mei-friend.github.io/cheatsheet/)
documents selection, shortcuts and shareable URLs. Avoid guessing keyboard
modifiers during the live demo; use the visible menus.

## Source images: prepare this before class

The hosted editor requires web-accessible images from a CORS-compatible server.
Relative filesystem paths in the notebook project do not automatically become
web resources. Its [facsimile guide](https://mei-friend.github.io/docs/advanced/facsimile/)
supplies a Beethoven example and explains selection/zone editing.

The release notebook can write a separate **mei-friend transfer copy** with
absolute URLs to a locally served page, leaving the canonical MEI untouched.
The supplied preview server adds CORS headers and serves only the edition
folder on loopback. Browser local-network restrictions may still apply. Use
this route only after rehearsal; the notebook-side source plus local MEI
open/save is the dependable fallback. Do not publish a transfer copy containing
localhost URLs.

When reconciling a transfer-copy save, restore its original graphic targets
from the recorded transfer manifest, then compare and validate. Do not blindly
overwrite `work.mei`. The round-trip checker reports changes to IDs, references,
graphics and musical structure; it cannot establish source fidelity.

GitHub integration is optional after the core Git introduction. The seminar's
short route uses the existing VS Code repository; students do not need to
authorise a second GitHub client to finish this ten-minute comparison.
