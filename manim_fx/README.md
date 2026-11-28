# manim_fx — free animated equations & graphs for the shorts

Code-driven motion-graphics "beats" (animated graphs and equations, the 3Blue1Brown
look) that you drop into a What If Lab / Beyond Obvious short so the explainer *moves*
instead of sitting on a static card. Built on **Manim Community** — 100% free and
open-source. No paid tools.

The clip is driven entirely by a **JSON config**, so you change the physics, the curve,
the labels and the colours without editing any code.

Output is **1080×1920 @ 30 fps** (the studio's vertical-shorts format), so a beat
composites straight into an episode.

## Install (free)
```bash
# Python 3.11 or 3.12 is recommended (prebuilt wheels for Manim's deps)
pip install manim

# system libraries:
#   macOS:   brew install ffmpeg pango cairo pkg-config
#   Ubuntu:  sudo apt-get install ffmpeg libcairo2-dev libpango1.0-dev pkg-config
# optional — LaTeX-typeset equations (otherwise a clean plain-text caption is used):
#   macOS:   brew install --cask mactex-no-gui      (or basictex)
#   Ubuntu:  sudo apt-get install texlive-latex-extra texlive-fonts-recommended dvisvgm
```

## Render
```bash
cd manim_fx
python render.py --config configs/whatiflab_moon_tides.json --out out/moon.mp4
# fast half-res check:
python render.py --config configs/whatiflab_moon_tides.json --out out/moon_preview.mp4 --preview
```

## Change the content (no code)
Edit a file in `configs/` (or copy one). Fields:

| field | meaning |
|---|---|
| `title`, `subtitle` | top text |
| `relationship` | the model. `{"kind":"power","coeff":c,"power":p}` → `y = c·xᵖ` (e.g. `power:-3` for tidal force ∝ 1/d³), or `{"kind":"linear","slope":m,"intercept":b}`. No arbitrary code is evaluated. |
| `x_range`,`y_range` | `[min, max, step]` for each axis |
| `x_label`, `y_label` | axis captions |
| `highlight_x`, `highlight_label` | where the tracer dot stops, and its marker |
| `readout_name` | label shown before the live number |
| `equation_text` | plain-text caption (always works) |
| `equation_tex` | LaTeX caption, used when a TeX install is present; falls back to `equation_text` |
| `final_line` | closing beat |
| `colors` | `bg / axis / curve / hilite / ink` hex overrides |

To make a new beat for another episode, copy `whatiflab_moon_tides.json`, change the
numbers and labels, and render.

## How it fits the pipeline
`render.py` emits a standalone 1080×1920 `.mp4`. Use it as an insert/B-roll beat inside
a short (overlay it on a segment, or cut to it for the "here's the physics" moment).
Keep beats short and meaningful — motion that explains, not decoration.

## Notes
- Every label in the clip is defined by the config, so what's on screen always matches
  the script.
- The sample uses **relative** tidal force (normalised to 1 at the Moon's current
  distance) so the axis numbers stay clean and the 1/d³ shape is the point.
