# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy",
#   "opencv-python-headless<5",
#   "scikit-image",
# ]
# ///
"""Apply the qualified two-seed Chroma band selector to a brothy-bowl image.

The two candidates must come from chroma-zimage at strength 0.125 with seeds 0
and 1. For each candidate, this offline compositor tests a frozen grid of
high-frequency cutoffs, keeps variants that pass all three fidelity gates, and
selects the largest RGB RMS change. Ties prefer seed 0 and then the smaller
high-period cutoff. The low-period cutoff is 32 pixels, and every transition
uses a 20% cosine taper in all YCrCb channels.

The qualified scope is narrow: 1024 x 1024 brothy-bowl photographs from the
dated GPT Image 2.5 Flare and Sunburst models. The utility does not need the
source model as an input. It writes a new metadata-free PNG plus a JSON report
that binds the inputs, selected parameters, metrics, and output by SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import cv2
import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)

LOW_PERIOD_PX = 32.0
HIGH_PERIODS_PX = (
    4.0,
    5.0,
    6.0,
    6.5,
    7.0,
    7.25,
    7.5,
    7.75,
    8.0,
    8.5,
    9.0,
    9.5,
    10.0,
    10.5,
    11.0,
    11.5,
    12.0,
    14.0,
    16.0,
)
QUALITY_GATES = {"psnr_db": 30.0, "ssim": 0.90, "edge_f1": 0.75}
QUALIFIED_SIZE = (1024, 1024)
TRANSITION_FRACTION = 0.20


@dataclass(frozen=True)
class Selection:
    image: np.ndarray
    seed: int
    high_period_px: float
    metrics: dict[str, float]
    output_rms_delta: float


def _lowpass(radius: np.ndarray, period_px: float) -> np.ndarray:
    cutoff = 1.0 / period_px
    inner = cutoff * (1.0 - TRANSITION_FRACTION)
    outer = cutoff * (1.0 + TRANSITION_FRACTION)
    mask = np.ones(radius.shape, dtype=np.float32)
    mask[radius >= outer] = 0.0
    transition = (radius > inner) & (radius < outer)
    mask[transition] = 0.5 + 0.5 * np.cos(np.pi * (radius[transition] - inner) / (outer - inner))
    return mask


def _frequency_radius(shape: tuple[int, int]) -> np.ndarray:
    height, width = shape
    if height <= 0 or width <= 0:
        raise ValueError("image dimensions must be positive")
    fy = np.fft.fftfreq(height)[:, None]
    fx = np.fft.fftfreq(width)[None, :]
    return np.sqrt(fx * fx + fy * fy)


def candidate_band_mask(shape: tuple[int, int], high_period_px: float) -> np.ndarray:
    """Return the candidate-frequency weight for one high cutoff."""
    radius = _frequency_radius(shape)
    if high_period_px not in HIGH_PERIODS_PX:
        raise ValueError(f"unsupported high period: {high_period_px}")
    return (1.0 - _lowpass(radius, LOW_PERIOD_PX)) * _lowpass(radius, high_period_px)


def _validate_pair(source: np.ndarray, candidate: np.ndarray) -> None:
    if source.shape != candidate.shape:
        raise ValueError("source and candidate shapes differ")
    if source.ndim != 3 or source.shape[2] != 3:
        raise ValueError("source and candidates must be three-channel BGR images")
    if source.dtype != np.uint8 or candidate.dtype != np.uint8:
        raise ValueError("source and candidates must use uint8 samples")


def restore_source_band(source: np.ndarray, candidate: np.ndarray, high_period_px: float) -> np.ndarray:
    """Keep candidate frequencies in one band and source frequencies elsewhere."""
    _validate_pair(source, candidate)
    source_ycc = cv2.cvtColor(source, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    candidate_ycc = cv2.cvtColor(candidate, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    mask = candidate_band_mask(source.shape[:2], high_period_px)
    source_ffts = tuple(np.fft.fft2(source_ycc[:, :, channel]) for channel in range(3))
    candidate_deltas = tuple(np.fft.fft2(candidate_ycc[:, :, channel]) - source_ffts[channel] for channel in range(3))
    return _compose_band(source_ycc, source_ffts, candidate_deltas, mask)


def _compose_band(
    source_ycc: np.ndarray,
    source_ffts: tuple[np.ndarray, ...],
    candidate_deltas: tuple[np.ndarray, ...],
    mask: np.ndarray,
) -> np.ndarray:
    output_ycc = source_ycc.copy()
    for channel in range(3):
        restored = np.fft.ifft2(source_ffts[channel] + mask * candidate_deltas[channel]).real
        output_ycc[:, :, channel] = np.clip(np.rint(restored), 0, 255)
    return cv2.cvtColor(output_ycc.astype(np.uint8), cv2.COLOR_YCrCb2BGR)


def _reference_edges(ref_gray: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    edges = cv2.Canny(ref_gray, 100, 200) > 0
    near = cv2.dilate(edges.astype(np.uint8), np.ones((3, 3), dtype=np.uint8)) > 0
    return edges, near, int(edges.sum())


def _edge_f1_gray(ref_gray: np.ndarray, cand_gray: np.ndarray) -> float:
    return _edge_f1_from_reference(_reference_edges(ref_gray), cand_gray)


def _edge_f1_from_reference(reference: tuple[np.ndarray, np.ndarray, int], cand_gray: np.ndarray) -> float:
    ref_edges, ref_near, ref_count = reference
    cand_edges = cv2.Canny(cand_gray, 100, 200) > 0
    cand_near = cv2.dilate(cand_edges.astype(np.uint8), np.ones((3, 3), dtype=np.uint8)) > 0
    cand_count = int(cand_edges.sum())
    if ref_count == 0 and cand_count == 0:
        return 1.0
    if ref_count == 0 or cand_count == 0:
        return 0.0
    precision = float((cand_edges & ref_near).sum()) / cand_count
    recall = float((ref_edges & cand_near).sum()) / ref_count
    return 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0


def quality_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    """Measure the frozen grayscale and tolerant-edge quality gates."""
    _validate_pair(reference, candidate)
    peak_signal_noise_ratio, structural_similarity = _metric_functions()
    ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    cand_gray = cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)
    return {
        "psnr_db": float(peak_signal_noise_ratio(ref_gray, cand_gray, data_range=255)),
        "ssim": float(structural_similarity(ref_gray, cand_gray, data_range=255)),
        "edge_f1": _edge_f1_gray(ref_gray, cand_gray),
    }


def _rms_delta(left: np.ndarray, right: np.ndarray) -> float:
    delta = left.astype(np.float32) - right.astype(np.float32)
    return float(np.sqrt(np.mean(delta * delta)))


def _metric_functions() -> tuple[Callable[..., float], Callable[..., float]]:
    from skimage import metrics

    peak_signal_noise_ratio = cast(
        "Callable[..., float]",
        metrics.peak_signal_noise_ratio,  # pyright: ignore[reportUnknownMemberType]
    )
    structural_similarity = cast(
        "Callable[..., float]",
        metrics.structural_similarity,  # pyright: ignore[reportUnknownMemberType]
    )
    return peak_signal_noise_ratio, structural_similarity


def select_source_band(source: np.ndarray, candidates: tuple[np.ndarray, np.ndarray]) -> Selection:
    """Choose the quality-positive seed and cutoff with the largest RGB delta."""
    if source.shape[:2] != QUALIFIED_SIZE:
        raise ValueError(f"qualified source size is {QUALIFIED_SIZE[1]} x {QUALIFIED_SIZE[0]}")
    if len(candidates) != 2:
        raise ValueError("exactly two candidates are required")
    for candidate in candidates:
        _validate_pair(source, candidate)
    best: Selection | None = None
    source_ycc = cv2.cvtColor(source, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    source_ffts = tuple(np.fft.fft2(source_ycc[:, :, channel]) for channel in range(3))
    radius = _frequency_radius(source.shape[:2])
    highpass = 1.0 - _lowpass(radius, LOW_PERIOD_PX)
    masks = {period: highpass * _lowpass(radius, period) for period in HIGH_PERIODS_PX}
    source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    reference_edges = _reference_edges(source_gray)
    peak_signal_noise_ratio, structural_similarity = _metric_functions()
    for seed, candidate in enumerate(candidates):
        candidate_ycc = cv2.cvtColor(candidate, cv2.COLOR_BGR2YCrCb).astype(np.float32)
        candidate_deltas = tuple(
            np.fft.fft2(candidate_ycc[:, :, channel]) - source_ffts[channel] for channel in range(3)
        )
        for high_period_px in HIGH_PERIODS_PX:
            output = _compose_band(source_ycc, source_ffts, candidate_deltas, masks[high_period_px])
            output_gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
            psnr_db = float(peak_signal_noise_ratio(source_gray, output_gray, data_range=255))
            if psnr_db < QUALITY_GATES["psnr_db"]:
                continue
            ssim = float(structural_similarity(source_gray, output_gray, data_range=255))
            if ssim < QUALITY_GATES["ssim"]:
                continue
            edge_f1 = _edge_f1_from_reference(reference_edges, output_gray)
            if edge_f1 < QUALITY_GATES["edge_f1"]:
                continue
            selection = Selection(
                image=output,
                seed=seed,
                high_period_px=high_period_px,
                metrics={"psnr_db": psnr_db, "ssim": ssim, "edge_f1": edge_f1},
                output_rms_delta=_rms_delta(source, output),
            )
            if best is None or _selection_key(selection) > _selection_key(best):
                best = selection
    if best is None:
        raise ValueError("no seed and cutoff combination passes all quality gates")
    return best


def _selection_key(selection: Selection) -> tuple[float, int, float]:
    return selection.output_rms_delta, -selection.seed, -selection.high_period_px


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
    parser.add_argument("candidate_seed0", type=Path, help="Chroma 0.125 seed-0 candidate")
    parser.add_argument("candidate_seed1", type=Path, help="Chroma 0.125 seed-1 candidate")
    parser.add_argument("output", type=Path, help="New metadata-free PNG path")
    parser.add_argument("--report", type=Path, help="Selection report path; defaults to OUTPUT.png.json")
    args = parser.parse_args()

    source_path = args.source.resolve()
    candidate_paths = (args.candidate_seed0.resolve(), args.candidate_seed1.resolve())
    output_path = args.output.resolve()
    report_path = args.report.resolve() if args.report else output_path.with_suffix(output_path.suffix + ".json")
    if report_path == output_path:
        raise ValueError("report path must differ from output path")
    if output_path.exists():
        raise FileExistsError(output_path)
    if report_path.exists():
        raise FileExistsError(report_path)
    source = _read_bgr(source_path)
    candidates = (_read_bgr(candidate_paths[0]), _read_bgr(candidate_paths[1]))
    selection = select_source_band(source, candidates)
    _write_new_png(output_path, selection.image)
    report = {
        "format_version": 1,
        "method": "two-seed-quality-adaptive-chroma-band",
        "candidate_profile": {"backend": "chroma-zimage", "strength": 0.125, "seeds": [0, 1]},
        "qualified_size": list(QUALIFIED_SIZE),
        "high_period_grid_px": list(HIGH_PERIODS_PX),
        "transition_fraction": TRANSITION_FRACTION,
        "source_path": str(source_path),
        "source_sha256": _sha256(source_path),
        "candidate_paths": [str(path) for path in candidate_paths],
        "candidate_sha256s": [_sha256(path) for path in candidate_paths],
        "output_path": str(output_path),
        "output_sha256": _sha256(output_path),
        "selected_seed": selection.seed,
        "low_period_px": LOW_PERIOD_PX,
        "high_period_px": selection.high_period_px,
        "metrics": selection.metrics,
        "output_rms_delta": selection.output_rms_delta,
        "quality_gates": QUALITY_GATES,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    log.info(
        "wrote %s seed=%s band=%s-%s report=%s output_sha256=%s",
        output_path,
        selection.seed,
        LOW_PERIOD_PX,
        selection.high_period_px,
        report_path,
        report["output_sha256"],
    )
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
