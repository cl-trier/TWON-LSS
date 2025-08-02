import typing
import datetime

import pytest

from twon_lss.schemas import User, Post, Interaction, InteractionTypes


@pytest.fixture
def users() -> typing.List[User]:
    return [User(), User(), User(), User()]


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
            content="Text Post P01 | Minimal post, no interactions or comments",
        ),
        Post(
            user=users[1],
            content="Text Post P02 | Post with interaction, but no comment",
            interactions=[
                Interaction(user=users[0], type=InteractionTypes.read),
                Interaction(user=users[0], type=InteractionTypes.like),
            ],
        ),
        Post(
            user=users[2],
            content="Text Post P03 | Full-featured post",
            interactions=[
                Interaction(user=users[0], type=InteractionTypes.read),
                Interaction(user=users[0], type=InteractionTypes.like),
                Interaction(user=users[1], type=InteractionTypes.read),
                Interaction(user=users[3], type=InteractionTypes.read),
            ],
            comments=[Post(user=users[3], content="Text Comment C01 on Post P01")],
        ),
        Post(
            user=users[3],
            content="Post P04 | With multiple comments",
            interactions=[
                Interaction(user=users[0], type=InteractionTypes.read),
                Interaction(user=users[2], type=InteractionTypes.read),
            ],
            comments=[
                Post(user=users[0], content="Comment C02 on Post P04"),
                Post(user=users[2], content="Comment C03 on Post P04"),
            ],
        ),
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
