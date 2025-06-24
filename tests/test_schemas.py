import typing

import pytest
import rich

from twon_lss.schemas import Feed, Post, User


@pytest.fixture
def feed(posts: typing.List["Post"]):
    return Feed(items=posts)


def test_feed(feed: Feed):
    rich.print(feed)


def test_user_feed(users: typing.List["User"], feed: Feed):
    rich.print(feed.get_items_by_user(users[0]))
