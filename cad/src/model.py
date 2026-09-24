"""HelioLite parametric model (build123d).

Run:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl.
"""
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # "example_length": 100.0,
}


def build():
    from build123d import Box  # noqa: F401  (placeholder until the real model lands)
    raise NotImplementedError("Model not yet developed. See docs/02-concept.md")


if __name__ == "__main__":
    part = build()
    out = Path(__file__).resolve().parents[1]
    from build123d import export_step, export_stl
    export_step(part, str(out / "step" / "heliolite.step"))
    export_stl(part, str(out / "stl" / "heliolite.stl"))
