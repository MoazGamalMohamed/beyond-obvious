"""
Animated-relationship beat for What If Lab / Beyond Obvious shorts.

Renders a short, vertical (1080x1920 @ 30 fps) motion-graphics clip that draws a
labelled set of axes, grows a curve y = f(x), then sweeps a tracer dot along it to
highlight one key value -- the "3Blue1Brown" look that makes an explainer feel
professional instead of showing a static card.

Everything here is free / open-source (Manim Community). The clip renders with just
`pip install manim` (+ ffmpeg/cairo/pango) -- NO LaTeX required: axis numbers, the live
readout and the caption all use Pango text. If a TeX distribution *is* present and the
config provides `equation_tex`, the bottom caption is upgraded to a LaTeX-typeset
equation automatically.

The physics, the curve and all labels are driven by a plain JSON config
(see configs/*.json), so the content can be changed without touching this file.

Matches the studio's vertical-shorts format: W,H = 1080,1920 and FPS = 30.
render.py pins a true 9:16 scene frame (frame_width 8.0 x frame_height 14.222),
which the layout below fills.
"""

from __future__ import annotations

import shutil

from manim import (
    Scene, Axes, Text, MathTex, Dot, VGroup,
    Create, Write, FadeIn, FadeOut, Indicate,
    ValueTracker, always_redraw,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
)

# --- brand-neutral, high-contrast palette (defined here, overridable per config) ---
BG = "#0E1116"        # near-black studio background
AXIS = "#9AA3AF"      # muted grey axes
CURVE = "#4CC9F0"     # bright accent for the curve
HILITE = "#F7B32B"    # highlight / marker colour
INK = "#F5F7FA"       # text

_HAS_LATEX = shutil.which("latex") is not None


def _f_from_config(rel: dict):
    """Build the relationship function f(x) from a named, non-eval'd model.

    Supported kinds (all standard, parameterised):
      power:  y = coeff * x**power     (e.g. power=-3 -> tidal force ~ 1/d^3)
      linear: y = slope * x + intercept
    """
    kind = rel.get("kind", "power")
    if kind == "power":
        coeff = float(rel.get("coeff", 1.0))
        power = float(rel.get("power", -3.0))
        return lambda x: coeff * (x ** power)
    if kind == "linear":
        slope = float(rel.get("slope", 1.0))
        intercept = float(rel.get("intercept", 0.0))
        return lambda x: slope * x + intercept
    raise ValueError(f"Unknown relationship kind: {kind!r}")


def _int_ticks(lo: float, hi: float):
    """Integer tick positions inside [lo, hi], capped to keep the frame clean."""
    out, v = [], 1
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            out.append(v)
        v += 1
    return out[:4]


def _fit(m, w: float):
    """Scale a mobject down (never up) so it fits within width w (scene units)."""
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


DEFAULT_CFG = {
    "title": "What if the Moon vanished?",
    "subtitle": "Tidal force vs. distance",
    "x_label": "Distance d  (Moon = 1)",
    "y_label": "Tidal force  (relative)",
    "relationship": {"kind": "power", "coeff": 1.0, "power": -3.0},
    "x_range": [0.7, 3.0, 0.5],
    "y_range": [0.0, 3.0, 1.0],
    "highlight_x": 1.0,
    "highlight_label": "the Moon",
    "readout_name": "force",
    "equation_text": "F_tidal  ∝  1 / d³",
    "equation_tex": r"F_{\text{tidal}} \;\propto\; \dfrac{1}{d^{3}}",
    "final_line": "Remove it → the tides go flat.",
    "colors": {},
}


class RelationshipScene(Scene):
    """Config-driven animated relationship. Pass cfg=... or it uses DEFAULT_CFG."""

    def __init__(self, cfg: dict | None = None, **kwargs):
        super().__init__(**kwargs)
        self.cfg = {**DEFAULT_CFG, **(cfg or {})}
        c = self.cfg.get("colors", {})
        self.col_bg = c.get("bg", BG)
        self.col_axis = c.get("axis", AXIS)
        self.col_curve = c.get("curve", CURVE)
        self.col_hilite = c.get("hilite", HILITE)
        self.col_ink = c.get("ink", INK)

    def construct(self):
        cfg = self.cfg
        self.camera.background_color = self.col_bg
        f = _f_from_config(cfg["relationship"])

        xr, yr = cfg["x_range"], cfg["y_range"]
        hx = float(cfg["highlight_x"])

        # --- title / subtitle / live readout (top block) ---
        title = _fit(Text(cfg["title"], color=self.col_ink, weight="BOLD", font_size=56), 7.2)
        title.to_edge(UP, buff=0.5)
        subtitle = _fit(Text(cfg["subtitle"], color=self.col_axis, font_size=36), 7.0)
        subtitle.next_to(title, DOWN, buff=0.25)

        # --- axes (large, centred for the tall vertical frame); numbers via Text ---
        ax = Axes(
            x_range=xr, y_range=yr,
            x_length=6.2, y_length=7.4,
            tips=False,
            axis_config={"color": self.col_axis, "stroke_width": 3, "include_numbers": False},
        )
        ax.move_to(DOWN * 0.3)

        ticks = VGroup()
        for xv in _int_ticks(xr[0], xr[1]):
            ticks.add(Text(str(xv), color=self.col_axis, font_size=26)
                      .next_to(ax.c2p(xv, yr[0]), DOWN, buff=0.14))
        for yv in _int_ticks(yr[0], yr[1]):
            ticks.add(Text(str(yv), color=self.col_axis, font_size=26)
                      .next_to(ax.c2p(xr[0], yv), LEFT, buff=0.14))

        x_label = _fit(Text(cfg["x_label"], color=self.col_axis, font_size=30), 7.0)
        x_label.next_to(ax, DOWN, buff=0.45).set_x(ax.get_x())
        y_label = Text(cfg["y_label"], color=self.col_axis, font_size=30)
        y_label.rotate(PI / 2).next_to(ax, LEFT, buff=0.12)

        curve = ax.plot(f, x_range=[xr[0], xr[1]], color=self.col_curve, stroke_width=7)

        # --- live tracer: dot + vertical guide + numeric readout (all LaTeX-free) ---
        tracker = ValueTracker(xr[1])

        def _pt():
            x = tracker.get_value()
            return ax.c2p(x, f(x))

        dot = always_redraw(lambda: Dot(_pt(), color=self.col_hilite, radius=0.11))
        vline = always_redraw(
            lambda: ax.get_vertical_line(_pt(), color=self.col_hilite, stroke_width=2)
        )

        def _readout():
            val = f(tracker.get_value())
            g = VGroup(
                Text(f"{cfg['readout_name']} =", color=self.col_ink, font_size=36),
                Text(f"{val:.2f}", color=self.col_hilite, weight="BOLD", font_size=36),
            ).arrange(RIGHT, buff=0.18)
            return g.next_to(subtitle, DOWN, buff=0.32).set_x(0)

        readout = always_redraw(_readout)

        # --- bottom caption: LaTeX if available, else Pango text ---
        caption = _fit(self._make_caption(), 7.2).to_edge(DOWN, buff=0.6)

        # ---------------- animation timeline (~10 s beat) ----------------
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.5)
        self.play(Create(ax), FadeIn(ticks), FadeIn(x_label), FadeIn(y_label), run_time=1.2)
        self.play(Create(curve), run_time=1.3)
        self.add(vline, dot, readout)
        self.wait(0.2)

        # sweep the tracer from far away in to the highlighted value
        self.play(tracker.animate.set_value(hx), run_time=1.7)

        marker = Text(cfg["highlight_label"], color=self.col_hilite, font_size=32)
        marker.next_to(ax.c2p(hx, f(hx)), RIGHT, buff=0.22)
        self.play(FadeIn(marker, shift=RIGHT * 0.2), Indicate(dot, color=self.col_hilite),
                  run_time=0.8)
        self.play(Write(caption), run_time=1.0)
        self.wait(0.6)

        # final beat
        final = _fit(Text(cfg["final_line"], color=self.col_ink, weight="BOLD", font_size=44), 7.2)
        final.move_to(caption)
        self.play(FadeOut(caption), FadeIn(final, shift=UP * 0.2), run_time=0.8)
        self.wait(0.8)

    def _make_caption(self):
        tex = self.cfg.get("equation_tex")
        if tex and _HAS_LATEX:
            try:
                return MathTex(tex, color=self.col_ink, font_size=54)
            except Exception:
                pass  # fall back to plain text on any TeX error
        return Text(self.cfg.get("equation_text", ""), color=self.col_ink, font_size=40)
