import typing

import pytest
import rich

from twon_lss.schemas import Feed, Post, User


@pytest.fixture
def feed(posts: typing.List[Post]):
    return Feed(posts)


def test_feed(feed: Feed):
    rich.print(feed)


def test_user_feed(users: typing.List[User], feed: Feed):
    rich.print(feed.get_items_by_user(users[0]))


def test_post_add_comment(posts: typing.List[Post]):
    assert len(posts[1].get_interactions()["read"]) == 1
    posts[1].add_comment(posts[0])
    assert len(posts[1].get_interactions()["read"]) == 0
