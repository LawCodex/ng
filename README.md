# Nigeria (NG) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Federal legislation of the Federal Republic of Nigeria, in **English**, from official sources:

* the **Constitution of the Federal Republic of Nigeria, 1999** — Federal Ministry of Justice edition
  "with the First, Second and Third Alterations" (2010–2011);
* the **Acts published by the National Assembly** of Nigeria on its website (nass.gov.ng,
  "Acts & Publications"), as enacted (not consolidated).

Retrieved 2026-10-13.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `acts/` | 161 |
| `constitution/` | 1 |
| `constitution/alterations/` | 2 |
| **Total** | **164** |
<!-- /COUNTS -->

## Structure

```
constitution/constitution-1999.md         Constitution (MoJ edition, 1st-3rd alterations incorporated)
constitution/alterations/<slug>.md        Constitution alteration Acts published by the National Assembly
acts/<year>/<slug>.md                     Acts of the National Assembly (year = year in the Act's title)
```

File names are slugs of the official short title (e.g. `acts/2011/freedom-of-information-act-2011.md`).

Front matter: `identifier` is the National Assembly document number (`https://nass.gov.ng/documents/download/<n>`),
`year` is the year of the Act as given in its title, `status` is `unknown` (the source does not state whether an
Act has since been amended or repealed), `note` says when the text was obtained by OCR. A few entries published by
the National Assembly under "Acts & Publications" are titled as Bills (harmonised/assented texts); they are kept with
`type: bill`.

Headings: `PART`/`CHAPTER`/`SCHEDULE` become `##`/`###` headings; sections are headings `Section N`. Marginal notes
(side headings) of the printed Acts are kept where the PDF text layer places them, which is sometimes in the middle
of a section. Arrangements of sections (tables of contents) are kept as plain text.

## Sources

| Source | URL | Used for |
|---|---|---|
| National Assembly of Nigeria — Acts & Publications | https://nass.gov.ng/documents/magazine (JSON list: `/documents/magazine_track/`, files: `/documents/download/<id>`) | Acts, constitution alteration Acts |
| Federal Ministry of Justice — Nigerian Constitution | https://justice.gov.ng/nigerian-constitution/ → https://justice.gov.ng/wp-content/uploads/2020/09/Nigerian-Constitution.pdf | Constitution |

Notes on the sources:

* Many National Assembly PDFs are scans; their text was produced by OCR (tesseract, English) and contains
  recognition errors (marked `OCR` in the `note` field). Some PDFs carry a poor embedded text layer; pages whose
  text looked garbled were re-OCRed.
* The National Assembly's own copy of the 1999 Constitution (document 5820) is a defective print (the left margin of
  every line is cut off), so the Ministry of Justice edition is used instead. That PDF has a damaged page tree
  (poppler cannot open it); `pypdf` recovers all 209 pages, whose printed page numbers were checked to be in sequence.
* Documents that are not legislation (magazines, handbooks, motions) are skipped. One entry is a Word document and
  is converted with macOS `textutil`.

## Not covered / known gaps

* **This is not the full body of Nigerian federal law.** The National Assembly publishes only ~150 Acts (mostly
  1999–2017 plus a few 2025–2026 Acts). The official revised edition **Laws of the Federation of Nigeria 2004**
  (LFN, Caps A1–Z) is not hosted on any official Government website that could be found; the non-governmental
  PLAC mirror (placng.org/lawsofnigeria) and the AfricanLII/NigeriaLII site were deliberately **not** used (the
  latter's terms forbid bulk download).
* Constitution: the Fourth Alteration Acts (2017–2018) and the Fifth Alteration Acts (2023) are not incorporated
  and are not available from the sources used.
* No consolidation: Acts are as enacted; amendments are separate files.
* State laws, subsidiary legislation (regulations, orders) and Presidential executive orders are not included.
* The National Assembly's PDF of the Trade Union (Amendment) Act 2005 (document 5808) is corrupt (no extractable
  text) and is missing; duplicate uploads (e.g. Investments and Securities Act 2007) are kept once.
* 65 files were produced by OCR; 5 entries are Bill texts (`type: bill`).

## Copyright

Nigerian Acts and the Constitution are official texts of the Federal Republic of Nigeria, published by the
National Assembly and the Federal Ministry of Justice for public information; neither website states terms
restricting reuse. The Markdown conversion is provided as is, for information; the authoritative texts are the
official printed versions.

## Regenerating

```sh
python3 -m pip install -r scripts/requirements.txt   # plus poppler-utils and tesseract
python3 scripts/ng_fetch.py            # downloads to ../_raw/ng/ (cached) and writes the Markdown
python3 scripts/ng_readme.py           # updates the counts table above
```
