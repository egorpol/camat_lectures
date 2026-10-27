# Optional Continue configurations

Documentation-based examples, checked 25 October 2026; provider inference and
extension login have not been tested. Install Continue in VS Code, open its
Local Config with the configuration selector/gear, and merge one model entry
into the existing `models` list. Keep your other configuration.

- `continue-gemini.yaml`: personal Gemini Free Tier key, two named models.
- `continue-openrouter.yaml`: personal OpenRouter key, explicit free variant.
- `continue-ollama.yaml`: downloaded local model, no provider key.

The snippets use Chat/Edit/Apply roles and omit extra autocomplete/embedding
models. Begin with a Chat proposal and apply it manually, so an implicit extra
service is not needed to complete the task. An automatic edit/apply operation
can make additional model calls.

For cloud routes, set `GEMINI_API_KEY=...` or `OPENROUTER_API_KEY=...` in your
**personal** `~/.continue/.env` (Windows: corresponding user-profile directory).
These files contain only secret placeholders; never put real keys here.
The extension cannot obtain a key merely from an export in a terminal.

Sources: [local configuration](https://docs.continue.dev/customize/deep-dives/configuration),
[secrets](https://docs.continue.dev/faqs#local-config),
[configuration fields](https://docs.continue.dev/reference),
[Gemini](https://docs.continue.dev/customize/model-providers/top-level/gemini),
[OpenRouter](https://docs.continue.dev/customize/model-providers/top-level/openrouter),
[Ollama](https://docs.continue.dev/customize/model-providers/top-level/ollama).
