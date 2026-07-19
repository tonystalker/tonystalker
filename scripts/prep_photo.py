"""
prep_photo.py

One-time step, run locally whenever you swap your photo:
  1. Remove the background (rembg) so only the subject remains.
  2. Boost local contrast with CLAHE so a flatly-lit face gets real
     highlights/shadows instead of converting to a dark blob.
  3. Composite onto pure white, then convert to grayscale, so the
     background maps to the blank end of the ASCII ramp.

Usage:
    python scripts/prep_photo.py source-photo.jpg
Writes:
    source-prepped.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(src_path: str, out_path: str = "source-prepped.png") -> None:
    src_bytes = Path(src_path).read_bytes()

    # 1. Remove background -> RGBA with subject isolated
    cutout_bytes = remove(src_bytes)
    cutout = Image.open(__import__("io").BytesIO(cutout_bytes)).convert("RGBA")

    # 2. CLAHE contrast boost on the RGB channels (subject only)
    rgb = np.array(cutout.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    boosted_rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    boosted = Image.fromarray(boosted_rgb).convert("RGBA")
    boosted.putalpha(cutout.getchannel("A"))

    # 3. Composite onto pure white, then flatten to grayscale
    canvas = Image.new("RGBA", boosted.size, (255, 255, 255, 255))
    canvas.alpha_composite(boosted)
    gray = canvas.convert("L")

    gray.save(out_path)
    print(f"wrote {out_path} ({gray.size[0]}x{gray.size[1]})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python scripts/prep_photo.py <photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
