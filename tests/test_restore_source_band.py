from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import restore_source_band as band


def _gray_bgr(values: np.ndarray) -> np.ndarray:
    return np.repeat(values[:, :, None], 3, axis=2).astype(np.uint8)


def _passing_metric(*args: object, **kwargs: object) -> float:
    return 100.0


def test_restoration_takes_candidate_midband_and_source_outside_band() -> None:
    size = 320
    yy, xx = np.mgrid[:size, :size]
    slow_wave = 12.0 * np.sin(2.0 * np.pi * xx / 64.0)
    middle_wave = 18.0 * np.sin(2.0 * np.pi * xx / 16.0)
    checker = np.where((xx + yy) % 2 == 0, 7.0, -7.0)
    source = _gray_bgr(np.clip(96.0 + slow_wave + checker, 0, 255))
    candidate = _gray_bgr(np.clip(176.0 + middle_wave, 0, 255))

    restored = band.restore_source_band(
        source,
        candidate,
        10.0,
    )
    expected = _gray_bgr(np.clip(96.0 + slow_wave + middle_wave + checker, 0, 255))

    assert np.max(np.abs(restored.astype(np.int16) - expected.astype(np.int16))) <= 1


@pytest.mark.parametrize(
    ("high_period_px", "high_transition_index", "shoulder_weight"),
    [
        (10.0, 32, 0.9157348061512727),
        (8.0, 40, 0.8535533905932737),
    ],
)
def test_candidate_mask_uses_the_frozen_cutoff_grid(
    high_period_px: float,
    high_transition_index: int,
    shoulder_weight: float,
) -> None:
    mask = band.candidate_band_mask((320, 320), high_period_px)

    assert mask[0, 0] == 0.0
    assert mask[0, 9] == pytest.approx(0.1464466094067262)
    assert mask[0, 10] == pytest.approx(0.5)
    assert mask[0, 20] == pytest.approx(1.0)
    assert mask[0, high_transition_index - 4] == pytest.approx(shoulder_weight)
    assert mask[0, high_transition_index] == pytest.approx(0.5)
    assert mask[0, 48] == 0.0


def test_restoration_rejects_an_unknown_cutoff() -> None:
    pixels = np.zeros((32, 32, 3), dtype=np.uint8)

    with pytest.raises(ValueError, match="unsupported high period"):
        band.restore_source_band(pixels, pixels.copy(), 13.0)


def test_restoration_rejects_a_shape_mismatch() -> None:
    source = np.zeros((32, 32, 3), dtype=np.uint8)
    candidate = np.zeros((32, 31, 3), dtype=np.uint8)

    with pytest.raises(ValueError, match="shapes differ"):
        band.restore_source_band(source, candidate, 10.0)


@pytest.mark.parametrize("dtype", [np.float32, np.uint16])
def test_restoration_rejects_non_uint8_samples(dtype: np.dtype) -> None:
    source = np.zeros((32, 32, 3), dtype=dtype)

    with pytest.raises(ValueError, match="uint8"):
        band.restore_source_band(source, source.copy(), 8.0)


def test_selector_prefers_the_quality_positive_candidate_with_more_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    size = 32
    _, xx = np.mgrid[:size, :size]
    source = _gray_bgr(np.full((size, size), 128.0))
    candidate0 = _gray_bgr(128.0 + 4.0 * np.sin(2.0 * np.pi * xx / 16.0))
    candidate1 = _gray_bgr(128.0 + 8.0 * np.sin(2.0 * np.pi * xx / 16.0))
    monkeypatch.setattr(band, "QUALIFIED_SIZE", (size, size))
    monkeypatch.setattr(band, "HIGH_PERIODS_PX", (8.0,))
    monkeypatch.setattr(band, "QUALITY_GATES", {"psnr_db": 0.0, "ssim": 0.0, "edge_f1": 0.0})
    monkeypatch.setattr(band, "_metric_functions", lambda: (_passing_metric, _passing_metric))

    selection = band.select_source_band(source, (candidate0, candidate1))

    assert selection.seed == 1
    assert selection.high_period_px == 8.0


def test_selector_breaks_an_exact_tie_by_seed_then_smaller_cutoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    size = 32
    _, xx = np.mgrid[:size, :size]
    source = _gray_bgr(np.full((size, size), 128.0))
    candidate = _gray_bgr(128.0 + 8.0 * np.sin(2.0 * np.pi * xx / 16.0))
    monkeypatch.setattr(band, "QUALIFIED_SIZE", (size, size))
    monkeypatch.setattr(band, "HIGH_PERIODS_PX", (8.0, 10.0))
    monkeypatch.setattr(band, "QUALITY_GATES", {"psnr_db": 0.0, "ssim": 0.0, "edge_f1": 0.0})
    monkeypatch.setattr(band, "_metric_functions", lambda: (_passing_metric, _passing_metric))

    selection = band.select_source_band(source, (candidate, candidate.copy()))

    assert selection.seed == 0
    assert selection.high_period_px == 8.0


def test_selector_rejects_an_unqualified_image_size() -> None:
    source = np.zeros((32, 32, 3), dtype=np.uint8)

    with pytest.raises(ValueError, match="qualified source size"):
        band.select_source_band(source, (source.copy(), source.copy()))


def test_writer_never_overwrites_an_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "restored.png"
    pixels = np.zeros((8, 8, 3), dtype=np.uint8)
    band._write_new_png(output, pixels)

    with pytest.raises(FileExistsError):
        band._write_new_png(output, pixels)


def test_selector_prepares_reference_edges_and_frequency_grid_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    size = 32
    yy, xx = np.mgrid[:size, :size]
    source = _gray_bgr(np.where((xx // 8 + yy // 8) % 2 == 0, 80, 180))
    candidate0 = _gray_bgr(source[:, :, 0].astype(float) + 8 * np.sin(2 * np.pi * xx / 16))
    candidate1 = _gray_bgr(source[:, :, 0].astype(float) + 12 * np.sin(2 * np.pi * xx / 16))
    calls = {"radius": 0, "reference_edges": 0}
    original_radius = band._frequency_radius
    original_reference_edges = band._reference_edges

    def frequency_radius(shape: tuple[int, int]) -> np.ndarray:
        calls["radius"] += 1
        return original_radius(shape)

    def reference_edges(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
        calls["reference_edges"] += 1
        result = original_reference_edges(gray)
        assert result[2] > 0
        return result

    monkeypatch.setattr(band, "QUALIFIED_SIZE", (size, size))
    monkeypatch.setattr(band, "HIGH_PERIODS_PX", (8.0, 10.0))
    monkeypatch.setattr(band, "QUALITY_GATES", {"psnr_db": 0.0, "ssim": 0.0, "edge_f1": 0.0})
    monkeypatch.setattr(band, "_metric_functions", lambda: (_passing_metric, _passing_metric))
    monkeypatch.setattr(band, "_frequency_radius", frequency_radius)
    monkeypatch.setattr(band, "_reference_edges", reference_edges)

    selection = band.select_source_band(source, (candidate0, candidate1))

    assert selection.image.shape == source.shape
    assert calls == {"radius": 1, "reference_edges": 1}


@pytest.mark.parametrize("failed_metric", ["psnr_db", "ssim", "edge_f1"])
def test_selector_rejects_each_failed_fidelity_gate(
    failed_metric: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    size = 32
    source = np.full((size, size, 3), 128, dtype=np.uint8)
    candidate = np.full_like(source, 132)
    monkeypatch.setattr(band, "QUALIFIED_SIZE", (size, size))
    monkeypatch.setattr(band, "HIGH_PERIODS_PX", (8.0,))
    values = {"psnr_db": 40.0, "ssim": 0.99, "edge_f1": 0.99}
    values[failed_metric] = band.QUALITY_GATES[failed_metric] - 0.01
    monkeypatch.setattr(
        band,
        "_metric_functions",
        lambda: (
            lambda *a, **k: values["psnr_db"],
            lambda *a, **k: values["ssim"],
        ),
    )
    monkeypatch.setattr(band, "_edge_f1_from_reference", lambda *a, **k: values["edge_f1"])

    with pytest.raises(ValueError, match="no seed and cutoff combination passes"):
        band.select_source_band(source, (candidate, candidate.copy()))


@pytest.mark.parametrize("bad_input", ["source", "candidate0", "candidate1"])
def test_selector_rejects_non_uint8_before_feature_preparation(
    bad_input: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    size = 32
    source = np.zeros((size, size, 3), dtype=np.uint8)
    candidate0 = source.copy()
    candidate1 = source.copy()
    if bad_input == "source":
        source = source.astype(np.float32)
    elif bad_input == "candidate0":
        candidate0 = candidate0.astype(np.float32)
    else:
        candidate1 = candidate1.astype(np.float32)
    monkeypatch.setattr(band, "QUALIFIED_SIZE", (size, size))

    with pytest.raises(ValueError, match="uint8"):
        band.select_source_band(source, (candidate0, candidate1))
