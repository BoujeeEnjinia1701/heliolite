"""Licensing metadata and long-term archiving (STANDARDS sections 16 and 17). Run from the repo root.

    python .kit/archive.py reuse                     # REUSE.toml, LICENSES/, REUSE workflow, badges
    python .kit/archive.py zenodo                    # one-license CITATION.cff and the Zenodo DOI badge
    python .kit/archive.py zenodo --doi 10.5281/zenodo.NNN   # after the first archive: cite the concept DOI

`reuse` writes REUSE.toml from project.yaml (hardware and software licenses), copies or downloads the
license texts into LICENSES/, adds the REUSE check workflow and puts the REUSE and Software Heritage
badges on the README badge line. `zenodo` names a single license in CITATION.cff (Zenodo rejects a list),
adds the Zenodo DOI badge (needs the GitHub repository ID: gh, or --repo-id) and, with --doi, records the
concept DOI (the one that always resolves to the latest version). Both are safe to run again.
"""
import argparse, re, shutil, subprocess, sys
from pathlib import Path
import yaml

ROOT = Path.cwd()
KIT = Path(__file__).resolve().parent
AUTHOR = "Amish Chadha <amish@designmolecule.com>"

WORKFLOW = """# Checks that every file carries copyright and license information (REUSE Specification).
name: REUSE
on: [push, pull_request]
jobs:
  reuse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: fsfe/reuse-action@v5
"""

SOFTWARE_PATHS = ('["**/*.py", "**/*.sh", "**/*.js", "**/*.ipynb", "**/*.html", "**/*.j2", "**/*.css", '
                  '"firmware/**", ".github/workflows/**", ".claude/**", ".kit/requirements.txt", "requirements.txt"]')


def project():
    pm = yaml.safe_load((ROOT / "project.yaml").read_text()) or {}
    lic = pm.get("licenses") or {}
    hw, sw = lic.get("hardware"), lic.get("software")
    repo = str(pm.get("repo", ""))
    if not repo or "/" not in repo:
        sys.exit("project.yaml needs repo: <owner>/<name>")
    if not (hw or sw):
        sys.exit("project.yaml needs licenses: hardware and/or software")
    return pm, repo, hw, sw


def year():
    r = subprocess.run(["git", "log", "--reverse", "--format=%ad", "--date=format:%Y"], cwd=ROOT,
                       capture_output=True, text=True).stdout.split()
    return r[0] if r else "2026"


def reuse_toml(repo, hw, sw):
    y = year()
    main = hw or sw
    t = [ "version = 1",
          f'SPDX-PackageName = "{repo.split("/")[1]}"',
          f'SPDX-PackageSupplier = "{AUTHOR}"',
          f'SPDX-PackageDownloadLocation = "https://github.com/{repo}"', "",
          f"# Designs, documentation, media and data: {main}",
          "[[annotations]]", 'path = "**"', 'precedence = "closest"',
          f'SPDX-FileCopyrightText = "{y} {AUTHOR}"', f'SPDX-License-Identifier = "{main}"', "" ]
    if hw and sw and hw != sw:
        t += [ f"# Software: scripts, firmware, notebooks, web viewers, workflows and agent commands: {sw}",
               "[[annotations]]", f"path = {SOFTWARE_PATHS}", 'precedence = "closest"',
               f'SPDX-FileCopyrightText = "{y} {AUTHOR}"', f'SPDX-License-Identifier = "{sw}"', "",
               f"# CAD and electronics sources are hardware design files, even when written as Python: {hw}",
               "[[annotations]]", 'path = ["cad/**", "electronics/**"]',
               f'SPDX-FileCopyrightText = "{y} {AUTHOR}"', f'SPDX-License-Identifier = "{hw}"', "" ]
    if (ROOT / ".kit/fonts").is_dir():
        t += [ "# Bundled IBM Plex fonts", "[[annotations]]", 'path = ".kit/fonts/**"', 'precedence = "override"',
               'SPDX-FileCopyrightText = "2017 IBM Corp."', 'SPDX-License-Identifier = "OFL-1.1"', "" ]
    return "\n".join(t)


def license_texts(ids):
    d = ROOT / "LICENSES"
    d.mkdir(exist_ok=True)
    for i in ids:
        f = d / f"{i}.txt"
        if f.exists():
            continue
        r = subprocess.run([sys.executable, "-m", "reuse", "download", i], cwd=ROOT, capture_output=True, text=True)
        if not f.exists() and i == "OFL-1.1" and (ROOT / ".kit/fonts/OFL.txt").exists():
            shutil.copy(ROOT / ".kit/fonts/OFL.txt", f)
        if not f.exists():
            sys.exit(f"could not fetch the {i} license text (pip install reuse, and network): {r.stderr.strip()[-200:]}")


def add_badges(badges):
    p = ROOT / "README.md"
    s = p.read_text(encoding="utf-8")
    new = [b for key, b in badges if key not in s]
    if not new:
        return 0
    lines = s.split("\n")
    idx = next((i for i, l in enumerate(lines[:12]) if l.startswith("![TRL") or "img.shields.io/badge" in l), None)
    if idx is None:
        lines.insert(2, " ".join(new) + "\n")
    else:
        lines[idx] = lines[idx].rstrip() + " " + " ".join(new)
    p.write_text("\n".join(lines), encoding="utf-8")
    return len(new)


def cmd_reuse(a):
    pm, repo, hw, sw = project()
    ids = [x for x in dict.fromkeys([hw, sw]) if x]
    if (ROOT / ".kit/fonts").is_dir():
        ids.append("OFL-1.1")
    license_texts(ids)
    (ROOT / "REUSE.toml").write_text(reuse_toml(repo, hw, sw))
    wf = ROOT / ".github/workflows/reuse.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text(WORKFLOW)
    gh = f"https://github.com/{repo}"
    n = add_badges([
        ("reuse.yml/badge.svg", f"[![REUSE compliant]({gh}/actions/workflows/reuse.yml/badge.svg)]({gh}/actions/workflows/reuse.yml)"),
        ("softwareheritage.org/badge", f"[![Archived in Software Heritage](https://archive.softwareheritage.org/badge/origin/{gh}/)]"
                                       f"(https://archive.softwareheritage.org/browse/origin/?origin_url={gh})"),
    ])
    r = subprocess.run([sys.executable, "-m", "reuse", "lint", "-q"], cwd=ROOT, capture_output=True, text=True)
    print(f"REUSE files written for {repo} ({', '.join(ids)}); {n} badge(s) added; "
          + ("reuse lint passes" if r.returncode == 0 else "reuse lint FAILS: run `reuse lint` to see why"))
    return r.returncode


def cmd_zenodo(a):
    pm, repo, hw, sw = project()
    c = ROOT / "CITATION.cff"
    t = c.read_text(encoding="utf-8")
    m = re.search(r"^license:\n((?:  - .+\n)+)", t, re.M)
    if m:
        first = m.group(1).split("\n")[0].split("- ", 1)[1].strip()
        t = t.replace(m.group(0), f"license: {first}\n")
        print(f"CITATION.cff now names one license ({first}); Zenodo rejects a list")
    if a.doi:
        if not re.fullmatch(r"10\.\d{4,9}/\S+", a.doi):
            sys.exit(f"not a DOI: {a.doi}")
        if re.search(r"^doi:", t, re.M):
            t = re.sub(r"^doi:.*$", f'doi: "{a.doi}"', t, flags=re.M)
        else:
            t = re.sub(r"^(repository-code:)", f'doi: "{a.doi}"\n\\1', t, count=1, flags=re.M) \
                if re.search(r"^repository-code:", t, re.M) else t.rstrip("\n") + f'\ndoi: "{a.doi}"\n'
        print(f"CITATION.cff cites the concept DOI {a.doi}")
    c.write_text(t, encoding="utf-8")
    rid = a.repo_id
    if not rid and shutil.which("gh"):
        rid = subprocess.run(["gh", "api", f"repos/{repo}", "-q", ".id"], capture_output=True, text=True).stdout.strip()
    if rid:
        n = add_badges([("zenodo.org/badge", f"[![DOI](https://zenodo.org/badge/{rid}.svg)](https://zenodo.org/badge/latestdoi/{rid})")])
        print("Zenodo DOI badge added" if n else "Zenodo DOI badge already present")
    else:
        print("GitHub repository ID unknown (install gh or pass --repo-id); DOI badge not added")
    return 0


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest="cmd", required=True)
sub.add_parser("reuse", help="REUSE.toml, LICENSES/, REUSE workflow, REUSE and Software Heritage badges")
z = sub.add_parser("zenodo", help="one-license CITATION.cff, DOI badge, concept DOI")
z.add_argument("--doi", help="concept DOI from Zenodo, for example 10.5281/zenodo.23048670")
z.add_argument("--repo-id", help="GitHub repository ID for the DOI badge (found with gh if omitted)")
a = ap.parse_args()
sys.exit(cmd_reuse(a) if a.cmd == "reuse" else cmd_zenodo(a))
