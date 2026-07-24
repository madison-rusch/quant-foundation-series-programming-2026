"""Reference tests for present_value against hand-computed textbook values."""

from __future__ import annotations

import numpy as np
import pytest

from present_value import present_value


def test_discrete_known_value() -> None:
    # FV=1000, r=5%, t=10: 1000 / 1.05**10 = 613.913253...
    assert np.isclose(present_value(1000.0, 0.05, 10), 613.9132535407591)


def test_continuous_known_value() -> None:
    # FV=1000, r=5%, t=10: 1000 * exp(-0.5) = 606.530659...
    assert np.isclose(
        present_value(1000.0, 0.05, 10, continuous=True), 606.5306597126334
    )


def test_zero_years_returns_face_value() -> None:
    assert np.isclose(present_value(1000.0, 0.05, 0), 1000.0)


def test_zero_rate_is_identity() -> None:
    assert np.isclose(present_value(1000.0, 0.0, 42), 1000.0)


def test_vectorized_over_horizons() -> None:
    pv = present_value(1000.0, 0.05, np.array([0, 10]))
    assert np.allclose(pv, [1000.0, 613.9132535407591])


def test_scalar_inputs_return_float() -> None:
    assert isinstance(present_value(1000.0, 0.05, 10), float)


def test_negative_years_raises() -> None:
    with pytest.raises(ValueError):
        present_value(1000.0, 0.05, -1)


def test_rate_below_minus_one_raises() -> None:
    with pytest.raises(ValueError):
        present_value(1000.0, -1.5, 10)


def test_nan_input_raises() -> None:
    with pytest.raises(ValueError):
        present_value(np.nan, 0.05, 10)
