#!/usr/bin/env python3
"""Sliding-window image slicer for high-accuracy OCR/proofreading.

Problem: LLM vision input compresses large images, losing stroke-level detail
in dense Chinese text. Visually similar characters become indistinguishable.

Solution: Pre-slice source images into overlapping crops at native resolution.
Each slice is small enough that the LLM sees characters at full detail.

Usage:
    # Slice all images in a directory (auto-calibrate on first image)
    python scripts/slice_images.py images/originals/ch04/

    # Slice with explicit parameters (skip calibration)
    python scripts/slice_images.py images/originals/ch04/ --window-height 600 --overlap 100

    # Slice a single image
    python scripts/slice_images.py images/originals/ch04/page_01.png

Output:
    Creates a `slices/` subdirectory next to the input with numbered crops
    and a manifest.json mapping slices back to source images.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_image_dimensions(img_path: Path) -> tuple[int, int]:
    """Return (width, height) of an image using ImageMagick identify."""
    result = subprocess.run(
        ["identify", "-format", "%w %h", str(img_path)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split()
    return int(w), int(h)


def detect_content_region(img_path: Path, width: int, height: int) -> tuple[int, int]:
    """Detect the vertical range containing actual text content.

    Skips phone UI elements (status bar at top, navigation at bottom)
    by looking for the transition from dark/grey (UI) to light (page background).

    Returns (top_y, bottom_y) of the content region.
    """
    # Sample a vertical strip down the center of the image
    # Look for brightness transitions to find content boundaries
    center_x = width // 2
    strip_width = 20

    result = subprocess.run(
        ["convert", str(img_path),
         "-crop", f"{strip_width}x{height}+{center_x}+0",
         "-resize", f"1x{height}!",
         "-depth", "8",
         "txt:-"],
        capture_output=True, text=True, check=True,
    )

    # Parse pixel brightness values
    brightnesses = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith("#"):
            continue
        # Format: "0,Y: (R,G,B,...)"
        try:
            parts = line.split("(")[1].split(")")[0].split(",")
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            brightness = (r + g + b) / 3
            brightnesses.append(brightness)
        except (IndexError, ValueError):
            continue

    if not brightnesses:
        return 0, height

    # Content region is where brightness is consistently high (light background)
    # UI regions tend to be darker (status bar, nav bar)
    threshold = 200  # Light background threshold

    # Find top boundary: first row where brightness stays high
    top_y = 0
    for i in range(len(brightnesses)):
        if i + 10 < len(brightnesses):
            window = brightnesses[i:i + 10]
            if all(b > threshold for b in window):
                top_y = max(0, i - 5)  # Small margin
                break

    # Find bottom boundary: last row where brightness stays high
    bottom_y = height
    for i in range(len(brightnesses) - 1, 0, -1):
        if i - 10 >= 0:
            window = brightnesses[i - 10:i]
            if all(b > threshold for b in window):
                bottom_y = min(height, i + 5)
                break

    # Sanity check: content region should be at least 60% of image
    if (bottom_y - top_y) < height * 0.6:
        return 0, height

    return top_y, bottom_y


def slice_image(
    img_path: Path,
    output_dir: Path,
    window_height: int,
    overlap: int,
    content_top: int,
    content_bottom: int,
    img_width: int,
) -> list[dict]:
    """Slice a single image into overlapping vertical crops.

    Returns list of slice metadata dicts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = img_path.stem
    content_height = content_bottom - content_top
    step = window_height - overlap
    slices = []

    y = content_top
    idx = 0
    while y < content_bottom:
        remaining = content_bottom - y
        h = min(window_height, remaining)

        # If remaining is too small (< 30% of window), merge with previous
        if h < window_height * 0.3 and idx > 0:
            break

        slice_name = f"{stem}_s{idx:02d}.png"
        slice_path = output_dir / slice_name

        subprocess.run(
            ["convert", str(img_path),
             "-crop", f"{img_width}x{h}+0+{y}",
             "+repage",
             str(slice_path)],
            check=True,
        )

        slices.append({
            "slice": slice_name,
            "source": img_path.name,
            "index": idx,
            "crop": {"x": 0, "y": y, "width": img_width, "height": h},
        })

        y += step
        idx += 1

    return slices


def calibrate_window(img_path: Path, content_top: int, content_bottom: int, img_width: int) -> int:
    """Determine optimal window height by checking character readability.

    Strategy: Start with a reasonable default based on image dimensions.
    The window should show ~6-8 lines of text at native resolution.

    For typical phone screenshots (1080-1440px wide), 500-700px height works well.
    For higher-res images, scale proportionally.

    Returns recommended window_height.
    """
    content_height = content_bottom - content_top

    # Heuristic: window should be ~20-25% of content height
    # This typically gives 6-8 lines of text
    candidate = int(content_height * 0.22)

    # Clamp to reasonable range
    min_h = max(300, img_width // 4)
    max_h = min(800, content_height // 3)
    candidate = max(min_h, min(max_h, candidate))

    return candidate


def process_directory(
    input_dir: Path,
    window_height: int | None,
    overlap: int | None,
) -> None:
    """Process all images in a directory."""
    image_extensions = {".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"}
    images = sorted(
        f for f in input_dir.iterdir()
        if f.suffix in image_extensions
    )

    if not images:
        print(f"No images found in {input_dir}")
        sys.exit(1)

    output_dir = input_dir / "slices"
    output_dir.mkdir(exist_ok=True)

    # Calibrate on first image if parameters not provided
    first_img = images[0]
    img_width, img_height = get_image_dimensions(first_img)
    content_top, content_bottom = detect_content_region(first_img, img_width, img_height)

    print(f"Image dimensions: {img_width}x{img_height}")
    print(f"Content region: y={content_top} to y={content_bottom} "
          f"({content_bottom - content_top}px)")

    if window_height is None:
        window_height = calibrate_window(first_img, content_top, content_bottom, img_width)
        print(f"Auto-calibrated window height: {window_height}px")

    if overlap is None:
        overlap = max(50, int(window_height * 0.18))
        print(f"Auto-calibrated overlap: {overlap}px")

    manifest = {
        "parameters": {
            "window_height": window_height,
            "overlap": overlap,
            "content_region": {"top": content_top, "bottom": content_bottom},
            "image_dimensions": {"width": img_width, "height": img_height},
        },
        "images": {},
    }

    total_slices = 0
    for img_path in images:
        w, h = get_image_dimensions(img_path)
        # Reuse content region from first image (same source = same layout)
        ct, cb = content_top, content_bottom
        if h != img_height:
            ct, cb = detect_content_region(img_path, w, h)

        slices = slice_image(
            img_path, output_dir, window_height, overlap, ct, cb, w,
        )
        manifest["images"][img_path.name] = slices
        total_slices += len(slices)
        print(f"  {img_path.name}: {len(slices)} slices")

    # Write manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {len(images)} images → {total_slices} slices")
    print(f"Output: {output_dir}/")
    print(f"Manifest: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Slice images into overlapping crops for high-accuracy OCR"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Image file or directory of images",
    )
    parser.add_argument(
        "--window-height", "-w",
        type=int, default=None,
        help="Crop window height in pixels (auto-calibrate if omitted)",
    )
    parser.add_argument(
        "--overlap", "-o",
        type=int, default=None,
        help="Overlap between adjacent slices in pixels (auto if omitted)",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()

    if input_path.is_file():
        # Single image: create slices/ next to it
        output_dir = input_path.parent / "slices"
        w, h = get_image_dimensions(input_path)
        ct, cb = detect_content_region(input_path, w, h)

        wh = args.window_height
        if wh is None:
            wh = calibrate_window(input_path, ct, cb, w)
        ov = args.overlap or max(50, int(wh * 0.18))

        slices = slice_image(input_path, output_dir, wh, ov, ct, cb, w)
        manifest = {
            "parameters": {"window_height": wh, "overlap": ov},
            "images": {input_path.name: slices},
        }
        with open(output_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"{input_path.name}: {len(slices)} slices → {output_dir}/")

    elif input_path.is_dir():
        process_directory(input_path, args.window_height, args.overlap)
    else:
        print(f"Not found: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
