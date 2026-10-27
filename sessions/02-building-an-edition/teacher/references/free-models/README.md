# Dated model-access evidence

[openrouter-2026-10-25.json](openrouter-2026-10-25.json) is a filtered snapshot of
the public `GET https://openrouter.ai/api/v1/models` response. It records the
retrieval timestamp, SHA-256 of the original response, selection rule, model
IDs, prices, modalities, context and supported parameters. **No inference was
requested**. Availability and advertised capabilities are not functional tests.

The snapshot contains 17 `:free` entries with zero prompt/completion prices.
It includes specialists that are not suitable for the MEI editing task. The
[research handout](../../../../03-linking-and-editing/teacher/vscode-free-models.md) explains the chosen candidates,
account requirements, quotas and official documentary sources.

Refresh into a new file:

```sh
python tools/snapshot_free_models.py --output /tmp/free-models-new.json
```

The script is standard-library Python, needs no API key, performs only a public
catalogue GET, and refuses to overwrite an existing snapshot. The report's
human-readable conclusions are dated separately and need rechecking against
current provider/extension documentation before a later seminar.
