from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import restore_source_detail as detail


def _gray_bgr(values: np.ndarray) -> np.ndarray:
    return np.repeat(values[:, :, None], 3, axis=2).astype(np.uint8)


def test_restoration_takes_candidate_low_frequency_and_source_high_frequency() -> None:
    size = 128
    yy, xx = np.mgrid[:size, :size]
    checker = np.where((xx + yy) % 2 == 0, 12.0, -12.0)
    slow_wave = 16.0 * np.sin(2.0 * np.pi * xx / 64.0)
    source = _gray_bgr(np.clip(80.0 + checker, 0, 255))
    candidate = _gray_bgr(np.clip(160.0 + slow_wave, 0, 255))

    restored = detail.restore_source_detail(source, candidate)
    expected = _gray_bgr(np.clip(160.0 + slow_wave + checker, 0, 255))

    assert np.max(np.abs(restored.astype(np.int16) - expected.astype(np.int16))) <= 1


def test_restoration_rejects_a_shape_mismatch() -> None:
    source = np.zeros((32, 32, 3), dtype=np.uint8)
    candidate = np.zeros((32, 31, 3), dtype=np.uint8)

    with pytest.raises(ValueError, match="shapes differ"):
        detail.restore_source_detail(source, candidate)


@pytest.mark.parametrize("dtype", [np.float32, np.uint16])
def test_restoration_rejects_non_uint8_samples(dtype: np.dtype) -> None:
    source = np.zeros((32, 32, 3), dtype=dtype)

    with pytest.raises(ValueError, match="uint8"):
        detail.restore_source_detail(source, source.copy())


def test_candidate_mask_uses_the_frozen_transition() -> None:
    mask = detail.candidate_lowpass_mask((200, 200))

    assert mask[0, 0] == 1.0
    assert mask[0, 20] == pytest.approx(1.0)
    assert mask[0, 22] == pytest.approx(0.9045084971874737)
    assert mask[0, 25] == pytest.approx(0.5)
    assert mask[0, 28] == pytest.approx(0.0954915028125263)
    assert mask[0, 30] == 0.0


def test_writer_never_overwrites_an_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "restored.png"
    pixels = np.zeros((8, 8, 3), dtype=np.uint8)
    detail._write_new_png(output, pixels)

    with pytest.raises(FileExistsError):
        detail._write_new_png(output, pixels)
