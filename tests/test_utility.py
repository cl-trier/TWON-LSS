import typing
import datetime

import pytest

from twon_lss.utility import Noise, Decay


class TestNoise:
    @pytest.fixture
    def noise(self) -> Noise:
        return Noise()

    @pytest.fixture
    def noise_samples(self, noise: Noise, num_observations: int) -> typing.List[float]:
        return noise.draw_samples(num_observations)

    def test_noise_bounds(self, noise: Noise, noise_samples: typing.List[float]):
        assert noise.low <= min(noise_samples)
        assert max(noise_samples) <= noise.high

    def test_noise_distribution(self, noise: Noise, noise_samples: typing.List[float]):
        assert sum(noise_samples) / len(noise_samples) == pytest.approx(
            sum([noise.low, noise.high]) / 2, abs=1e-3
        )


class TestUtility:
    @pytest.fixture
    def decay(self) -> Decay:
        return Decay()

    def test_decay_abs_now(self, decay: Decay, ref_datetime: datetime.datetime):
        assert decay(ref_datetime, ref_datetime) == pytest.approx(1.0, abs=1e-3)

    def test_decay_abs_past(
        self,
        decay: Decay,
        ref_datetime: datetime.datetime,
        ref_timedelta: datetime.timedelta,
    ):
        assert decay(ref_datetime - ref_timedelta, ref_datetime) == pytest.approx(
            decay.minimum, abs=1e-3
        )
