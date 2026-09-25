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


TRL_NAMES = {1: "Basic principles observed", 2: "Technology concept formulated",
             3: "Proof of concept", 4: "Validated in the lab", 5: "Validated in a relevant environment",
             6: "System prototype demonstrated", 7: "System prototype in operational environment",
             8: "System complete and qualified", 9: "Proven in operation"}


def project_meta() -> dict:
    y = ROOT / "project.yaml"
    return yaml.safe_load(y.read_text()) if y.exists() else {}


def trl_check(docs) -> list[str]:
    """Verify that the evidence required for the claimed TRL exists (STANDARDS section 9)."""
    pm = project_meta()
    if "trl" not in pm:
        return ["project.yaml has no 'trl' field"]
    trl, errs = int(pm["trl"]), []
    if not 1 <= trl <= 9:
        return [f"trl {trl} must be between 1 and 9"]
    if int(pm.get("trl_target", trl)) < trl:
        errs.append("trl_target is below the current trl")
    by_type = {}
    for p, m, _ in docs:
        by_type.setdefault(str(m["doc_id"]).split("-")[1], []).append((p, m))
    def need(level, ok, what):
        if trl >= level and not ok:
            errs.append(f"TRL {trl} claimed but TRL {level} evidence is missing: {what}")
    need(1, "PRB" in by_type, "problem statement (PRB)")
    need(2, "PRC" in by_type and "REQ" in by_type, "precis (PRC) and requirements (REQ)")
    if trl >= 3:
        model = ROOT / "cad/src/model.py"
        need(3, "CAL" in by_type, "calculation note (CAL)")
        need(3, model.exists() and "NotImplementedError" not in model.read_text(), "working cad/src/model.py")
        need(3, any((ROOT / "cad/step").glob("*.step")), "STEP export in cad/step")
        need(3, any((ROOT / "cad/drawings").glob("*-DWG-*.svg")), "drawing sheet in cad/drawings")
        bom = ROOT / "bom/bom.csv"
        import csv
        rows = list(csv.DictReader(bom.open())) if bom.exists() else []
        need(3, rows and all((r.get("unit_cost_usd") or "").strip() for r in rows), "every BOM row priced")
    envs = [str(m.get("environment", "")) for _, m in by_type.get("TST", [])]
    need(4, bool(envs), "test report (TST)")
    need(4, len(list((ROOT / "build-log").glob("*.md"))) > 1, "build log entries")
    need(5, "relevant" in envs, "TST with environment: relevant")
    if trl >= 6:
        prc = [m for _, m in by_type.get("PRC", [])]
        need(6, any(m["status"] == "Released" and float(m["version"]) >= 1.0 for m in prc), "precis released at v1.0+")
        need(6, any(re.search(r"rev[A-Z]", f.name) or "Rev A" in f.read_text(errors="ignore")
                    for f in (ROOT / "cad/drawings").glob("*-DWG-*.svg")), "drawing at a lettered revision")
    for f in pm.get("trl_evidence") or []:
        if not (ROOT / f).exists():
            errs.append(f"trl_evidence lists a missing file: {f}")
    return errs


MEDIA_REQUIRED = ["media/concept-blueprint.png", "media/hero.png"]
MEDIA_OPTIONAL = ["media/cutaway.png", "media/exploded.png"]
BEYOND_CAP_PATHS = ["docs/05-tests", "docs/07-build", "bom/purchasing-checklist.md", "build-log/TEMPLATE.md"]


def phase_check(docs) -> tuple[list[str], list[str]]:
    """Portfolio phase rules (.kit/PHASE.yaml): TRL cap and concept media. Returns (errors, warnings)."""
    ph_file = KIT / "PHASE.yaml"
    if not ph_file.exists():
        return [], []
    ph = yaml.safe_load(ph_file.read_text()) or {}
    cap = int(ph.get("trl_cap", 9))
    pm = project_meta()
    errs, warns = [], []
    trl, target = int(pm.get("trl", 0) or 0), int(pm.get("trl_target", 0) or 0)
    if trl > cap:
        errs.append(f"trl {trl} exceeds the portfolio cap of TRL {cap} (.kit/PHASE.yaml)")
    if target > cap:
        errs.append(f"trl_target {target} exceeds the portfolio cap of TRL {cap} (.kit/PHASE.yaml)")
    tst = [p for p, m, _ in docs if "-TST-" in str(m["doc_id"])]
    extra = [str(p.relative_to(ROOT)) for p in tst] + [b for b in BEYOND_CAP_PATHS if (ROOT / b).exists()]
    if cap < 4 and extra:
        warns.append("work beyond the TRL %d cap is present (keep, but do not extend): %s" % (cap, ", ".join(sorted(set(extra)))))
    missing = [m for m in MEDIA_REQUIRED if not (ROOT / m).exists()]
    if trl >= int(ph.get("media_required_from_trl", 2)) and missing:
        msg = "concept media missing: " + ", ".join(missing) + " (see CLAUDE.md section 5)"
        (errs if trl >= 3 else warns).append(msg)
    return errs, warns


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
    terrs = trl_check(docs)
    if terrs:
        failed = True
        print("FAIL project.yaml TRL")
        for e in terrs:
            print(f"     - {e}")
    else:
        pm = project_meta()
        print(f"ok   TRL {pm['trl']} ({TRL_NAMES[int(pm['trl'])]}), target TRL {pm.get('trl_target', pm['trl'])}")
    perrs, pwarns = phase_check(docs)
    for w in pwarns:
        print(f"warn {w}")
    if perrs:
        failed = True
        print("FAIL portfolio phase")
        for e in perrs:
            print(f"     - {e}")
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
                          repo=repo_url(), trl=project_meta().get("trl"), trl_name=TRL_NAMES.get(int(project_meta().get("trl") or 0), ""), source=str(p.relative_to(ROOT)), commit=commit)
        for old in OUT.glob(f"{meta['doc_id']}_v*.pdf"):
            old.unlink()
        target = OUT / f"{meta['doc_id']}_v{meta['version']}.pdf"
        HTML(string=html, base_url=str(p.parent)).write_pdf(target)
        print(f"pdf  {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
