import abc
import typing

import pydantic

from twon_lss.utility import Noise
from twon_lss.schemas import User, Post, Feed, Network


class RankingInterfaceWeights(pydantic.BaseModel):
    """
    Configures the weighting system for ranking algorithms.

    The RankingInterfaceWeights class defines how different scoring components
    are weighted when calculating post rankings.

    Attributes:
        network (float): Weight applied to network-wide scoring components (default: 1.0).
        individual (float): Weight applied to individual user preference scoring (default: 1.0).

    """

    network: float = 1.0
    individual: float = 1.0


class RankingArgsInterface(abc.ABC, pydantic.BaseModel):
    """
    Abstract base class for ranking algorithm configuration.

    The RankingArgsInterface class provides a standardized configuration
    interface for ranking algorithms, including weighting systems, noise
    injection, and module-specific arguments. This ensures consistent
    configuration patterns across different ranking implementations.

    Attributes:
        weights (RankingInterfaceWeights): Weighting configuration for different scoring components (default: RankingInterfaceWeights()).
        noise (Noise): Noise injection configuration for score randomization (default: Noise()).

    """

    weights: RankingInterfaceWeights = pydantic.Field(
        default_factory=RankingInterfaceWeights
    )
    noise: Noise = pydantic.Field(default_factory=Noise)


class RankingInterface(abc.ABC, pydantic.BaseModel):
    """
    Abstract base class for ranking algorithms.

    The `RankingInterface` class provides a standardized framework for implementing
    ranking algorithms in the social media simulation. It defines the core ranking
    workflow that combines network-wide signals with individual user preferences,
    applies weighting and noise, and filters posts based on network connectivity.

    The ranking process follows these steps:
    1. Calculate global (network-wide) scores for all posts
    2. For each user, identify posts from their network neighbors
    3. Calculate individual user-specific scores for accessible posts
    4. Combine global and individual scores with configured weights
    5. Apply noise injection for score randomization

    Attributes:
        args (RankingArgsInterface): Configuration object containing weights, noise, and module-specific arguments (default: RankingArgsInterface()).
    """

    args: RankingArgsInterface = pydantic.Field(default_factory=RankingArgsInterface)

    def __call__(
        self, users: typing.List[User], feed: Feed, network: Network
    ) -> typing.Dict[typing.Tuple[User, Post], float]:
        """
        Rank posts for all users based on network and individual preferences.

        This method orchestrates the complete ranking process by computing
        global scores for all posts, then calculating personalized scores
        for each user based on their network connections and individual
        preferences.

        Args:
            users (List[User]): List of users to generate rankings for.
            feed (Feed): Feed containing all posts to be ranked.
            network (Network): Social network structure defining user connections.

        Returns:
            Dict[Tuple[User, Post], float]: Dictionary mapping (user, post) tuples
            to their respective ranking scores. Only includes posts visible to
            each user based on network connectivity.

        """
        # retrieve global score for each post
        # TODO parallelize on post level
        global_scores: typing.Dict[str, float] = {}
        for post in feed:
            global_scores[post.id] = self.get_network_score(post)

        # retrieve indivual score for visible (if is neighbor) post for each user
        # TODO parallelize on user level
        final_scores: typing.Dict[typing.Tuple[User, Post], float] = {}
        for user in users:
            for post in self.get_individual_posts(user, feed, network):
                individual_score = self.get_individual_score(user, post, feed)
                global_score = global_scores[post.id]

                combined_score = (
                    self.args.weights.individual * individual_score
                    + self.args.weights.network * global_score
                )

                final_scores[(user, post)] = self.args.noise() * combined_score

        return final_scores

    def get_individual_posts(self, user: User, feed: Feed, network: Network):
        """
        Filter posts visible to a specific user based on network connections.

        This method determines which posts a user can see by checking their
        network connections. Users can only see unread posts from their
        direct neighbors in the social network.

        Args:
            user (User): The user to filter posts for.
            feed (Feed): Feed containing all posts.
            network (Network): Social network structure.

        Returns:
            List[Post]: List of posts visible to the specified user.
        """
        return [
            post
            for neighbor in network.get_neighbors(user)
            for post in feed.get_unread_items_by_user(user).get_items_by_user(neighbor)
        ]

    def get_network_score(self, post: Post) -> float:
        """
        Calculate the weighted network-wide score for a post.

        This method computes the global ranking score for a post by calling
        the abstract _compute_network method and applying the configured
        network weight.

        Args:
            post (Post): The post to calculate the network score for.

        Returns:
            float: Weighted network score for the post.

        """
        return self.args.weights.network * self._compute_network(post)

    def get_individual_score(self, user: User, post: Post, feed: Feed) -> float:
        """
        Calculate the weighted individual user score for a post.

        This method computes the personalized ranking score for a user-post
        pair by calling the abstract _compute_individual method and applying
        the configured individual weight.

        Args:
            user (User): The user to calculate the individual score for.
            post (Post): The post to calculate the individual score for.
            feed (Feed): Feed containing all posts.

        Returns:
            float: Weighted individual score for the user-post pair.
        """
        return self.args.weights.individual * self._compute_individual(user, post, feed)

    @abc.abstractmethod
    def _compute_network(self, post: Post) -> float:
        """
        Abstract method for computing network-wide post scores.

        This method must be implemented by subclasses to define how posts
        are scored based on network-wide signals such as engagement metrics,
        viral potential, or content quality indicators.

        Args:
            post (Post): The post to calculate the network score for.

        Returns:
            float: Raw network score for the post (before weighting).

        Note:
            This method should return a raw score that will be weighted
            by the network weight configuration.
        """
        pass

    @abc.abstractmethod
    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:
        """
        Abstract method for computing individual user-post scores.

        This method must be implemented by subclasses to define how posts
        are scored based on individual user preferences, interests, or
        behavioral patterns.

        Args:
            user (User): The user to calculate the individual score for.
            post (Post): The post to calculate the individual score for.
            feed (Feed): Feed containing all posts.

        Returns:
            float: Raw individual score for the user-post pair (before weighting).

        Note:
            This method should return a raw score that will be weighted
            by the individual weight configuration.
        """
        pass
