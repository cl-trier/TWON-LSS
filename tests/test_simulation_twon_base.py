import math
import typing
import datetime

import pytest

from twon_lss.utility import Decay
from twon_lss.simulations.twon_base.ranker import Engagement


class TestRanker:
    @pytest.fixture
    def observations(
        self,
        ref_datetime: datetime.datetime,
        ref_timedelta: datetime.timedelta,
        num_observations: int,
    ) -> typing.List[datetime.datetime]:
        return [
            ref_datetime - (ref_timedelta * i / num_observations)
            for i in reversed(range(num_observations))
        ]

    def test_engagement_count_abs(
        self,
        observations: typing.List[datetime.datetime],
        ref_datetime: datetime.datetime,
        num_observations: int,
    ):
        assert (
            Engagement(log_normalize=False)(
                items=observations, reference_datetime=ref_datetime, decay=Decay()
            )
            == num_observations
        )

    def test_engagement_count_log(
        self,
        observations: typing.List[datetime.datetime],
        ref_datetime: datetime.datetime,
        num_observations: int,
    ):
        assert Engagement(log_normalize=True)(
            items=observations, reference_datetime=ref_datetime, decay=Decay()
        ) == math.log(num_observations)
