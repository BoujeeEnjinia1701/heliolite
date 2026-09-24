#!/usr/bin/env python3
"""Validate and render controlled documents to branded PDFs.

Usage (from the repo root):
    python .kit/render.py            # check and render every controlled doc
    python .kit/render.py --check    # check only, no PDFs (used in CI on every push)

A controlled document is any Markdown file whose front matter has a doc_id.
Output: docs/pdf/<doc_id>_v<version>.pdf (older versions of the same doc are removed;
they remain in Git history and in GitHub Releases).
"""
import re, subprocess, sys, datetime
from pathlib import Path

import yaml, markdown, jinja2

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
OUT = ROOT / "docs" / "pdf"
REQUIRED = ["doc_id", "title", "project", "doc_type", "version", "status", "date", "author", "license", "revisions"]
STATUSES = {"Draft", "In review", "Released", "Superseded"}
ID_RE = re.compile(r"^[A-Z]{3}-(PRC|PRB|REQ|CAL|DDR|BOM|DWG|TST|STD)-\d{3}$")
VER_RE = re.compile(r"^\d+\.\d+$")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def split(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def check(meta: dict, path: Path) -> list[str]:
    errs = [f"missing field '{k}'" for k in REQUIRED if k not in meta]
    if errs:
        return errs
    v = str(meta["version"])
    if not ID_RE.match(str(meta["doc_id"])):
        errs.append(f"doc_id '{meta['doc_id']}' does not match PRJ-TYP-NNN")
    if not VER_RE.match(v):
        errs.append(f"version '{v}' must look like 0.1 or 1.0 (quote it in YAML)")
    if meta["status"] not in STATUSES:
        errs.append(f"status '{meta['status']}' must be one of {sorted(STATUSES)}")
    revs = meta["revisions"] or []
    if not revs:
        errs.append("revisions is empty")
    else:
        last = str(revs[-1].get("version"))
        if last != v:
            errs.append(f"version {v} does not match newest revision row {last}")
        for r in revs:
            for k in ("version", "date", "author", "change"):
                if not r.get(k):
                    errs.append(f"revision row {r} is missing '{k}'")
    if meta["status"] == "Released" and v.startswith("0."):
        errs.append("a Released document must be version 1.0 or later")
    if "—" in path.read_text(encoding="utf-8"):
        errs.append("contains an em dash; restructure the sentence")
    return errs


def git(*args) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def repo_url() -> str:
    y = ROOT / "project.yaml"
    slug = yaml.safe_load(y.read_text())["slug"] if y.exists() else ROOT.name
    return f"github.com/BoujeeEnjinia1701/{slug}"


def controlled_docs():
    for p in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in p.relative_to(ROOT).parts[:-1]):
            continue
        meta, body = split(p)
        if meta and "doc_id" in meta:
            yield p, meta, body


def main():
    only_check = "--check" in sys.argv
    docs = list(controlled_docs())
    failed = False
    for p, meta, _ in docs:
        errs = check(meta, p)
        rel = p.relative_to(ROOT)
        if errs:
            failed = True
            print(f"FAIL {rel}")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"ok   {rel}  {meta['doc_id']} v{meta['version']} {meta['status']}")
    if failed:
        sys.exit(1)
    if only_check or not docs:
        return

    from weasyprint import HTML  # imported late so --check needs no system libs
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(KIT / "style"), autoescape=False)
    tpl = env.get_template("doc.html.j2")
    commit = git("rev-parse", "--short", "HEAD") or "uncommitted"
    OUT.mkdir(parents=True, exist_ok=True)
    for p, meta, body in docs:
        meta["version"] = str(meta["version"])
        for r in meta["revisions"]:
            r["version"] = str(r["version"])
        html_body = markdown.markdown(body, extensions=["tables", "fenced_code", "attr_list", "sane_lists", "toc"])
        html = tpl.render(m=meta, body=html_body, css=(KIT / "style" / "doc.css").as_uri(),
                          repo=repo_url(), source=str(p.relative_to(ROOT)), commit=commit)
        for old in OUT.glob(f"{meta['doc_id']}_v*.pdf"):
            old.unlink()
        target = OUT / f"{meta['doc_id']}_v{meta['version']}.pdf"
        HTML(string=html, base_url=str(p.parent)).write_pdf(target)
        print(f"pdf  {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
