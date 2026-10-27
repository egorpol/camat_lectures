# Schumann PDF preparation records — 25 October 2026

The [executed notebook](../02_pdf_preparation_recorded.ipynb) records the first
two guided CAMAT steps. The [student notebook](../../../notebooks/02_pdf_preparation.ipynb)
uses the small `schumann-edition-inputs.zip` next to it and prepares source
media at runtime. [Block guide](../../pdf-preparation.md).

These JSON files are reference copies of a real temporary project's outputs.
Their relative PDF/image paths describe that project, not this reference folder.
The PDFs, PNG and scan previews are excluded; run the notebook to obtain them.
Do not substitute a reference manifest for derivatives rendered with different
input bytes or settings. The next stage must review measure boxes on the actual
PNG that its pages.json identifies.

- page-mapping.json: original PDF page 8 → excerpt PDF page 1 → printed page 8;
  extraction metadata/recipe and both PDF hashes.
- pages.json: the actual CAMAT manifest, fixed image identity and five systems.
- measure-page-map.json: 21 labels/IDs, systems, page mapping and core scope.
- checkpoint.json: the verified handoff state before measure boxes/linking.
- environment.json and requirements.txt: fresh PyPI CAMAT 0.2.8 installation,
  Python/package versions, relevant module hashes and Poppler version.
- rerun-check.json: unchanged hashes after re-executing the notebook.

The saved executed notebook retains setup instructions and text outputs, but
clears image payloads from source-media cells. The input ZIP contains no PDFs or
images and retains the starter's upstream credits and ECL-2.0 license.
