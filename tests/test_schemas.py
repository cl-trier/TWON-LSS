import typing

import pytest
import rich

from twon_lss.schemas import Feed, Post, User


class TestFeed:
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


class TestUser:
    num_users: int = 100_000

    @pytest.fixture
    def users(self) -> typing.List[User]:
        return [User() for _ in range(TestUser.num_users)]

    def test_uniqueness(self, users: typing.List[User]):
        assert len([u.id for u in users]) == len(users)
