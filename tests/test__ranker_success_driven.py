import math
import typing
import datetime

import pytest

from twon_lss.ranking.success_driven import Decay, Noise, Engagement


TOL: float = 1e-3


class TestSuccessDriven:
    @pytest.fixture
    def num_observations(self) -> int:
        return 1_000_000

    @pytest.fixture
    def refeference_datetime(self) -> datetime.datetime:
        return datetime.datetime.now()

    @pytest.fixture
    def refeference_timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(days=3)

    @pytest.fixture
    def observations(
        self,
        refeference_datetime: datetime.datetime,
        refeference_timedelta: datetime.timedelta,
        num_observations: int,
    ) -> typing.List[datetime.datetime]:
        return [
            refeference_datetime - (refeference_timedelta * i / num_observations)
            for i in reversed(range(num_observations))
        ]

    @pytest.fixture
    def decay(self, refeference_timedelta: datetime.timedelta) -> Decay:
        return Decay(minimum=0.2, reference_timedelta=refeference_timedelta)

    @pytest.fixture
    def noise(self) -> Noise:
        return Noise(low=0.8, high=1.4)

    @pytest.fixture
    def noise_samples(self, noise: Noise, num_observations: int) -> typing.List[float]:
        return noise.draw_samples(num_observations)

    def test_decay_abs_now(self, decay: Decay, refeference_datetime: datetime.datetime):
        assert decay(refeference_datetime, refeference_datetime) == pytest.approx(
            1.0, abs=TOL
        )

    def test_decay_abs_past(
        self,
        decay: Decay,
        refeference_datetime: datetime.datetime,
        refeference_timedelta: datetime.timedelta,
    ):
        assert decay(
            refeference_datetime - refeference_timedelta, refeference_datetime
        ) == pytest.approx(decay.minimum, abs=TOL)

    def test_engagement_count_abs(
        self, observations: typing.List[datetime.datetime], num_observations: int
    ):
        assert (
            Engagement(func="count_based", log_normalize=False)(items=observations)
            == num_observations
        )

    def test_engagement_count_log(
        self, observations: typing.List[datetime.datetime], num_observations: int
    ):
        assert Engagement(func="count_based", log_normalize=True)(
            items=observations
        ) == math.log(num_observations)

    def test_noise_bounds(self, noise: Noise, noise_samples: typing.List[float]):
        assert noise.low <= min(noise_samples)
        assert max(noise_samples) <= noise.high

    def test_noise_distribution(self, noise: Noise, noise_samples: typing.List[float]):
        assert sum(noise_samples) / len(noise_samples) == pytest.approx(
            sum([noise.low, noise.high]) / 2, abs=TOL
        )
