# Demo E source

`buxtehude_op1_01_page1.mei` is page 1 (bars 1–15; DdT 11, printed page 3; BSB image 00013) of `11_buxtehude_sonatas_final/buxtehude_op1_01_sonata_f_major_corr.mei` from <https://github.com/egorpol/DdT_1_vol_11> at commit `7af4ae88286961bfc7a0bfb0df43baf931f93835`, MIT License (see `LICENSE`, copied from that repository). Two ties into bar 16 on the next page were removed. To rebuild it, download that file at that commit and run, from the repository root:

```sh
.venv/bin/python tools/extract_facsimile_page.py SOURCE.mei 1 sessions/01-why-encode-music/examples/facsimile/buxtehude_op1_01_page1.mei "NOTE"
```

The note text is in the comment at the top of the MEI file. The scan is not in this repository: the live page loads it from the Bayerische Staatsbibliothek's IIIF server (`bsb00023199`, CC BY-NC-SA 4.0).
