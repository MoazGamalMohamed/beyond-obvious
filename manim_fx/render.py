#!/usr/bin/env python3
"""Render a motion-graphics beat from a JSON config to a vertical MP4.

Output is 1080x1920 @ 30 fps -- the studio's vertical-shorts format
(W,H = 1080,1920 and FPS = 30) -- so the clip drops straight into an episode timeline.

Usage:
    python render.py --config configs/whatiflab_moon_tides.json --out out/moon.mp4
    python render.py --config configs/whatiflab_moon_tides.json --out out/moon_preview.mp4 --preview

Install (free / open-source):
    pip install manim         # Python 3.11 or 3.12 recommended (prebuilt wheels)
    # system libs: ffmpeg, cairo, pango  (see README.md)
    # optional, for LaTeX-typeset equations: a TeX distribution (else a plain-text
    # caption is used automatically)
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # allow running as a plain script or as a module

# vertical-shorts output format (1080x1920 @ 30 fps)
PIX_W, PIX_H, FPS = 1080, 1920, 30


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render an animated-relationship beat.")
    ap.add_argument("--config", type=Path, default=HERE / "configs" / "whatiflab_moon_tides.json",
                    help="JSON config describing the beat (default: the Moon/tides sample).")
    ap.add_argument("--out", type=Path, default=HERE / "out" / "beat.mp4",
                    help="Output .mp4 path.")
    ap.add_argument("--preview", action="store_true",
                    help="Render at half resolution for a fast check.")
    args = ap.parse_args(argv)

    cfg = json.loads(args.config.read_text(encoding="utf-8")) if args.config else None

    from manim import tempconfig
    from relationship_scene import RelationshipScene  # local import (sys.path set above)

    scale = 0.5 if args.preview else 1.0
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as workdir:
        settings = {
            "pixel_width": int(PIX_W * scale),
            "pixel_height": int(PIX_H * scale),
            # Pin a true 9:16 canvas (scene units). Without this, Manim keeps the
            # 16:9 default frame and squishes everything into the middle band.
            "frame_width": 8.0,
            "frame_height": 8.0 * PIX_H / PIX_W,  # 14.222 for 1080x1920
            "frame_rate": FPS,
            "format": "mp4",
            "media_dir": workdir,
            "disable_caching": True,
            "verbosity": "ERROR",
        }
        with tempconfig(settings):
            scene = RelationshipScene(cfg=cfg)
            scene.render()
            produced = Path(scene.renderer.file_writer.movie_file_path)
        shutil.copyfile(produced, args.out)

    print(f"OK  {args.out}  ({int(PIX_W * scale)}x{int(PIX_H * scale)} @ {FPS}fps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
