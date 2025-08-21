import typing
import datetime

import pytest

import networkx

from twon_lss.schemas import Feed, Post, User, Network, Interaction, InteractionTypes


class TestFeed:
    @pytest.fixture
    def feed(self, posts: typing.List[Post]) -> Feed:
        return Feed(posts)

    @pytest.fixture
    def empty_feed(self):
        return Feed()

    def test_create(self, feed: Feed, posts: typing.List[Post]):
        assert len(feed) == len(posts)
        assert list(feed) == posts

    def test_empty_feed(self, empty_feed: Feed):
        assert len(empty_feed) == 0
        assert list(empty_feed) == []

    def test_iterate(self, feed: Feed, posts: typing.List[Post]):
        feed_posts = []
        for post in feed:
            feed_posts.append(post)
        assert feed_posts == posts

    def test_indexing(self, feed: Feed, posts: typing.List[Post]):
        assert feed[0] == posts[0]
        assert feed[-1] == posts[-1]

    def test_append(self, empty_feed: Feed, posts: typing.List[Post]):
        empty_feed.append(posts[0])
        assert len(empty_feed) == 1
        assert empty_feed[0] == posts[0]

    def test_extend(self, empty_feed: Feed, posts: typing.List[Post]):
        empty_feed.extend(posts[:2])
        assert len(empty_feed) == 2
        assert list(empty_feed) == posts[:2]

    def test_get_items_by_user(self, users: typing.List[User], feed: Feed):
        user_feed = feed.get_items_by_user(users[0])
        assert len(user_feed) == 1  # Only one post by users[0] in conftest
        assert all(post.user == users[0] for post in user_feed)

    def test_get_unread_items_by_user(self, users: typing.List[User], feed: Feed):
        # users[0] has read post by users[1] and users[2] according to conftest
        unread_feed = feed.get_unread_items_by_user(users[0])
        # Should contain posts that users[0] hasn't read
        for post in unread_feed:
            assert users[0] not in post.reads


class TestUser:
    num_users: int = 100_000

    @pytest.fixture
    def users(self) -> typing.List[User]:
        return [User() for _ in range(TestUser.num_users)]

    @pytest.fixture
    def single_user(self) -> User:
        return User()

    def test_user_creation(self, single_user: User):
        assert single_user.id.startswith("user-")
        assert len(single_user.id) > 16  # UUID should make it longer

    def test_user_hash(self, single_user: User):
        user_hash = hash(single_user)
        assert isinstance(user_hash, int)
        assert hash(single_user) == user_hash

    def test_user_equality(self):
        user1 = User(id="test-123")
        user2 = User(id="test-123")
        user3 = User(id="test-456")

        assert user1.id == user2.id
        assert user1.id != user3.id

    def test_user_custom_id(self):
        custom_user = User(id="custom-123")
        assert custom_user.id == "custom-123"

    def test_uniqueness(self, users: typing.List[User]):
        assert len([u.id for u in users]) == len(users)


class TestPost:
    @pytest.fixture
    def basic_post(self, users: typing.List[User]) -> Post:
        return Post(user=users[0], content="Basic test post")

    def test_post_creation(self, basic_post: Post, users: typing.List[User]):
        assert basic_post.user == users[0]
        assert basic_post.content == "Basic test post"
        assert basic_post.id.startswith("post-")

    def test_post_hash(self, basic_post: Post):
        post_hash = hash(basic_post)
        assert isinstance(post_hash, int)
        assert hash(basic_post) == post_hash


class TestNetwork:
    @pytest.fixture
    def network(self, users: typing.List[User]) -> Network:
        graph = networkx.random_regular_graph(3, len(users))
        return Network.from_graph(graph, users)

    @pytest.fixture
    def small_network(self) -> Network:
        users = [User() for _ in range(4)]
        graph = networkx.Graph()
        graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
        return Network.from_graph(graph, users)

    @pytest.fixture
    def empty_network(self) -> Network:
        return Network()

    def test_empty_network_creation(self, empty_network: Network):
        assert len(empty_network) == 0
        assert list(empty_network) == []

    def test_network_from_graph(self, small_network: Network):
        assert len(small_network) == 4
        users = list(small_network)
        assert all(isinstance(user, User) for user in users)

    def test_network_iteration(self, small_network: Network):
        user_count = 0
        for user in small_network:
            assert isinstance(user, User)
            user_count += 1
        assert user_count == len(small_network)

    def test_get_neighbors(self, small_network: Network):
        users = list(small_network)
        for user in users:
            neighbors = small_network.neighbors[user]
            assert isinstance(neighbors, list)
            assert all(isinstance(neighbor, User) for neighbor in neighbors)
            # In a 4-node cycle, each node should have 2 neighbors
            assert len(neighbors) == 2

    def test_network_relabeling(self, users: typing.List[User]):
        graph = networkx.path_graph(len(users))
        network = Network.from_graph(graph, users)

        network_users = list(network)
        assert len(network_users) == len(users)
        assert all(user in users for user in network_users)
