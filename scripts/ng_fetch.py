#!/usr/bin/env python3
"""Nigeria: fetch Acts published by the National Assembly (nass.gov.ng, "Acts & Publications")
and convert them to Markdown.

Usage: python3 ng_fetch.py [--no-download]
Raw PDFs are cached in ../../_raw/ng/pdf (outside the repo)."""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ng_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "ng")
LIST_URL = "https://nass.gov.ng/documents/magazine_track/?draw=1&start=0&length=5000"
DL = "https://nass.gov.ng/documents/download/%s"
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
SKIP = re.compile(r"MAGAZINE|HANDBOOK|OPEN WEEK|^MOTION$", re.I)


def clean_title(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("CREDlT", "CREDIT").replace("JUDIClAL", "JUDICIAL")
    return t


def nice_title(t):
    small = {"and", "of", "the", "for", "to", "in", "on", "etc", "a", "an", "by", "with", "or", "relating"}
    words = t.split(" ")
    out = []
    for k, w in enumerate(words):
        lw = w.lower()
        if re.match(r"^\(?(nahcon|neco|no\.\d|ii|iii|iv)\)?,?$", lw):
            out.append(w.upper() if "no." not in lw else "(No.2),")
            continue
        if k and lw.strip("(),.") in small:
            out.append(lw)
        else:
            out.append(re.sub(r"[A-Za-z][A-Za-z']*", lambda m: m.group(0).capitalize(), lw))
    return " ".join(out).replace("Etc.", "etc.").replace(" ,", ",")


def main():
    os.makedirs(RAW, exist_ok=True)
    lp = os.path.join(RAW, "magazine_track.json")
    if "--no-download" not in sys.argv or not os.path.exists(lp):
        T.fetch(LIST_URL, lp + ".new", delay=1)
        os.replace(lp + ".new", lp)
    data = json.load(open(lp))["data"]
    seen = {}
    for row in data:
        title = clean_title(row[0])
        docid = row[6]
        if SKIP.search(title):
            continue
        if docid == "5820":
            # NASS print of the 1999 Constitution is defective (left margin cut off, letters
            # missing); the Ministry of Justice edition is used instead (moj_constitution()).
            continue
        pdf = os.path.join(RAW, "pdf", "%s.pdf" % docid)
        if "--no-download" not in sys.argv:
            if not T.fetch(DL % docid, pdf, delay=2, check_pdf=True, tries=2):
                alt = os.path.join(RAW, "pdf", "%s.bin" % docid)
                if T.fetch(DL % docid, alt, delay=2) and T.sniff(alt) in ("docx", "doc", "rtf"):
                    pdf = alt
        alt = os.path.join(RAW, "pdf", "%s.bin" % docid)
        if not os.path.exists(pdf) and os.path.exists(alt):
            pdf = alt
        if not os.path.exists(pdf) or (pdf.endswith(".pdf") and not T.pdf_ok(pdf)):
            print("MISSING/BAD", docid, title, flush=True)
            continue
        if "--download-only" in sys.argv:
            continue
        pages, ocr = T.doc_or_pdf_text(pdf, "eng", tmpdir=RAW)
        lines = T.clean_pages(pages)
        body = T.structure(lines, "en")
        nchar = sum(len(x) for x in body)
        if nchar < 300:
            print("EMPTY", docid, title, nchar)
            continue
        ym = re.findall(r"(19\d\d|20\d\d)", title)
        year = ym[-1] if ym else (row[1][:4] if row[1] and row[1][:4] != "0000" else "undated")
        nt = nice_title(title)
        if re.search(r"CONSTITUTION", title) and "ACT" not in title:
            nt = "Constitution of the Federal Republic of Nigeria, 1999"
            rel = "constitution/constitution-1999.md"
            typ = "constitution"
        elif re.search(r"^CONSTITUTION OF THE FEDERAL REPUBLIC.*ALTERATION", title):
            rel = "constitution/alterations/%s.md" % T.slug(title)
            typ = "constitutional_amendment"
        else:
            typ = "bill" if re.search(r"\bBILL\b", title) and not re.search(r"\bACT\b(?!\s*\(AMENDMENT\) BILL)", title.replace("ACT (AMENDMENT) BILL", "")) else "act"
            rel = "acts/%s/%s.md" % (year, T.slug(title))
        key = rel
        if key in seen:
            # duplicate upload: keep the longer text
            if seen[key] >= nchar:
                continue
        seen[key] = nchar
        meta = {
            "title": nt,
            "identifier": "NASS document %s" % docid,
            "type": typ,
            "jurisdiction": "ng",
            "language": "en",
            "year": year if year != "undated" else None,
            "status": "unknown",
            "source": DL % docid,
            "retrieved": RETRIEVED,
            "note": ("Text as published by the National Assembly (as enacted, not consolidated)" +
                     ("; text obtained by OCR of a scanned PDF" if ocr else "") +
                     ("; listed by NASS under Acts & Publications but titled as a Bill" if typ == "bill" else "")),
        }
        if typ == "constitution":
            meta["status"] = "in_force"
            meta["date"] = "1999-05-05"
            meta["note"] = ("Text of the 1999 Constitution as originally promulgated (Decree No. 24 of 1999), "
                            "as published by the National Assembly; alterations are in constitution/alterations/"
                            + ("; OCR" if ocr else ""))
        T.write_md(os.path.join(REPO, rel), meta, nt, body)
        print("OK", docid, rel, nchar, "OCR" if ocr else "", flush=True)


MOJ_CONST = "https://justice.gov.ng/wp-content/uploads/2020/09/Nigerian-Constitution.pdf"


def moj_constitution():
    """Federal Ministry of Justice edition of the 1999 Constitution 'with the First, Second and
    Third Alterations'. The file on the server has a damaged page tree (poppler cannot read it);
    pypdf recovers all 209 pages (checked: printed page numbers 1-160 are in sequence)."""
    import logging
    import pypdf
    logging.disable(logging.CRITICAL)
    dest = os.path.join(RAW, "moj_constitution.pdf")
    T.fetch(MOJ_CONST, dest, delay=1)
    r = pypdf.PdfReader(dest, strict=False)
    pages = [p.extract_text() or "" for p in r.pages]
    if len(pages) < 200:
        raise SystemExit("constitution PDF incomplete: %d pages" % len(pages))
    lines = T.clean_pages(pages)
    body = T.structure(lines, "en")
    meta = {
        "title": "Constitution of the Federal Republic of Nigeria, 1999",
        "identifier": "Constitution of the Federal Republic of Nigeria 1999 (Cap. C23 LFN 2004)",
        "type": "constitution", "jurisdiction": "ng", "language": "en", "date": "1999-05-05",
        "last_amended": "2011-03-04", "status": "in_force", "source": MOJ_CONST,
        "retrieved": RETRIEVED,
        "note": ("Federal Ministry of Justice edition 'with the First, Second and Third Alterations' (2010-2011); "
                 "the alteration Acts are reproduced at the end. Later alterations (Fourth Alteration Acts 2017/2018, "
                 "Fifth Alteration Acts 2023) are NOT incorporated."),
    }
    T.write_md(os.path.join(REPO, "constitution", "constitution-1999.md"), meta, meta["title"], body)
    print("OK constitution", sum(len(x) for x in body), flush=True)


if __name__ == "__main__":
    moj_constitution()
    main()
