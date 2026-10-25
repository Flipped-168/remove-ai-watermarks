# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy",
#   "opencv-python-headless<5",
# ]
# ///
"""Restore source detail above the qualified eight-pixel period cutoff.

This is the offline compositor qualified by OpenAI attempt 15. It combines one
source image with its already-regenerated candidate: the candidate supplies low
and medium spatial frequencies, while the source supplies frequencies above
1/8 cycle per pixel through a 20% cosine transition. The transform operates in
OpenCV YCrCb and writes a metadata-free PNG.

The qualified scope is deliberately narrow: 1024 x 1024, single-object studio
product photographs without people or text, after qwen-zimage at strength
0.09375 and seed 0. Provider-oracle verification is still required for every new
content class.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path

import cv2
import numpy as np

log = logging.getLogger(__name__)

PERIOD_PX = 8.0
TRANSITION_FRACTION = 0.20


def candidate_lowpass_mask(shape: tuple[int, int]) -> np.ndarray:
    """Return the qualified radial weight for candidate frequency coefficients."""
    height, width = shape
    if height <= 0 or width <= 0:
        raise ValueError("image dimensions must be positive")
    fy = np.fft.fftfreq(height)[:, None]
    fx = np.fft.fftfreq(width)[None, :]
    radius = np.sqrt(fx * fx + fy * fy)
    inner = (1.0 / PERIOD_PX) * (1.0 - TRANSITION_FRACTION)
    outer = (1.0 / PERIOD_PX) * (1.0 + TRANSITION_FRACTION)
    mask = np.ones(shape, dtype=np.float32)
    mask[radius >= outer] = 0.0
    transition = (radius > inner) & (radius < outer)
    mask[transition] = 0.5 + 0.5 * np.cos(np.pi * (radius[transition] - inner) / (outer - inner))
    return mask


def restore_source_detail(source: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    """Combine BGR uint8 SOURCE high frequencies with CANDIDATE low frequencies."""
    if source.shape != candidate.shape:
        raise ValueError("source and candidate shapes differ")
    if source.ndim != 3 or source.shape[2] != 3:
        raise ValueError("source and candidate must be three-channel BGR images")
    if source.dtype != np.uint8 or candidate.dtype != np.uint8:
        raise ValueError("source and candidate must use uint8 samples")

    source_ycc = cv2.cvtColor(source, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    candidate_ycc = cv2.cvtColor(candidate, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    mask = candidate_lowpass_mask(source.shape[:2])
    output_ycc = source_ycc.copy()
    for channel in range(3):
        source_fft = np.fft.fft2(source_ycc[:, :, channel])
        candidate_fft = np.fft.fft2(candidate_ycc[:, :, channel])
        restored = np.fft.ifft2(source_fft + mask * (candidate_fft - source_fft)).real
        output_ycc[:, :, channel] = np.clip(np.rint(restored), 0, 255)
    return cv2.cvtColor(output_ycc.astype(np.uint8), cv2.COLOR_YCrCb2BGR)


def _read_bgr(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"could not decode image: {path}")
    return image


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_new_png(path: Path, image: np.ndarray) -> None:
    if path.suffix.lower() != ".png":
        raise ValueError("output path must end in .png")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded, payload = cv2.imencode(".png", image)
    if not encoded:
        raise RuntimeError("OpenCV could not encode the restored image")
    with path.open("xb") as stream:
        stream.write(payload.tobytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original watermarked source image")
    parser.add_argument("candidate", type=Path, help="Already-regenerated clean candidate")
    parser.add_argument("output", type=Path, help="New metadata-free PNG path")
    args = parser.parse_args()

    source_path = args.source.resolve()
    candidate_path = args.candidate.resolve()
    output_path = args.output.resolve()
    source = _read_bgr(source_path)
    candidate = _read_bgr(candidate_path)
    restored = restore_source_detail(source, candidate)
    _write_new_png(output_path, restored)
    log.info(
        "wrote %s source_sha256=%s candidate_sha256=%s output_sha256=%s",
        output_path,
        _sha256(source_path),
        _sha256(candidate_path),
        _sha256(output_path),
    )
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
