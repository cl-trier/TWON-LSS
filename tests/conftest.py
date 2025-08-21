import typing
import datetime

import pytest

from twon_lss.schemas import User, Post


@pytest.fixture
def users() -> typing.List[User]:
    return [User() for _ in range(4)]


@pytest.fixture
def network(users: typing.List[User]) -> typing.List[typing.Tuple[User, User]]:
    return [
        (users[0], users[1]),
        (users[0], users[2]),
        (users[1], users[3]),
        (users[2], users[3]),
    ]


@pytest.fixture
def posts(users: typing.List[User]) -> typing.List[Post]:
    return [
        Post(
            user=users[0],
            content="Text Post P01 | Minimal post, no reads or likes",
        ),
        Post(
            user=users[1],
            content="Text Post P02 | Post with reads, but no likes",
            reads=[users[0], users[2]],
        ),
        Post(
            user=users[2],
            content="Text Post P03 | Full-featured post",
            reads=[users[0], users[2]],
            likes=[users[0], users[2]],
        )
    ]


@pytest.fixture
def num_observations() -> int:
    return 1_000_000


@pytest.fixture
def ref_datetime() -> datetime.datetime:
    return datetime.datetime.now()


@pytest.fixture
def ref_timedelta() -> datetime.timedelta:
    return datetime.timedelta(days=3)
