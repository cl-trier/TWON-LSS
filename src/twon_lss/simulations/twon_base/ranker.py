import statistics
import logging
import time
import random
import typing

from twon_lss.interfaces import RankerInterface, RankerArgsInterface

from twon_lss.schemas import User, Post, Feed
from twon_lss.schemas.network import Network
from twon_lss.utility import LLM


__all__ = ["Ranker", "RankerArgs"]


class RankerArgs(RankerArgsInterface):
    pass


class Ranker(RankerInterface):
    llm: LLM

    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        return len(post.likes)

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        try:
            return statistics.mean(
                self.llm.similarity(
                    post.content, [item.content for item in feed.get_items_by_user(user)]
                )
            )
        except Exception as e:
            logging.error(f"Error computing individual score: {e}")
            time.sleep(15)
            return 0.0
        

class RandomRanker(RankerInterface):
    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        return 0.0

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        return random.uniform(0, 1)
    

class LikeRanker(RankerInterface):
    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        return len(post.likes) + random.uniform(0, 1) # to prevent "chronological reading"

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        return 0.0
    

class UserLikeRanker(RankerInterface):
    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post, feed: Feed) -> float:
        return feed.get_like_count_by_user(post.user) + random.uniform(0, 1) # to prevent "chronological reading"

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        return 0.0

    def __call__(
        self, users: typing.List[User], feed: Feed, network: Network
    ) -> typing.Dict[typing.Tuple[User, Post], float]:
        logging.debug(f"{len(feed)=}")

        global_scores: typing.Dict[str, float] = {}
        for post in feed:
            global_scores[post.id] = self._compute_network(post, feed)

        # retrieve indivual score for visible (if is neighbor) post for each user
        final_scores: typing.Dict[typing.Tuple[User, Post], float] = {}
        for user in users:
            for post in self.get_individual_posts(user, feed, network):
                individual_score = random.uniform(0, 1)
                global_score = global_scores[post.id]

                combined_score = (
                    self.args.weights.individual * individual_score
                    + self.args.weights.network * global_score
                )

                final_scores[(user, post)] = self.args.noise() * combined_score

        return final_scores
    

class PersonalizedUserLikeRanker(RankerInterface):
    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post, feed: Feed) -> float:
        return 0.0

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        return feed.get_likes_given_to_user(user, post.user) + random.uniform(0, 1) # Add noise in case that there are no likes, liked user has multiple unread tweets, multiple users have same like count etc.

    def __call__(
        self, users: typing.List[User], feed: Feed, network: Network
    ) -> typing.Dict[typing.Tuple[User, Post], float]:
        logging.debug(f"{len(feed)=}")

        global_scores: typing.Dict[str, float] = {}
        for post in feed:
            global_scores[post.id] = self._compute_network(post, feed)

        # retrieve indivual score for visible (if is neighbor) post for each user
        final_scores: typing.Dict[typing.Tuple[User, Post], float] = {}
        for user in users:
            for post in self.get_individual_posts(user, feed, network):
                individual_score = self._compute_individual(user, post, feed)
                global_score = global_scores[post.id]

                combined_score = (
                    self.args.weights.individual * individual_score
                    + self.args.weights.network * global_score
                )

                final_scores[(user, post)] = self.args.noise() * combined_score

        return final_scores
    
    