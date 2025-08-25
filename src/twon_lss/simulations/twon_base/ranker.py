import statistics
import logging
import time
import random

from twon_lss.interfaces import RankerInterface, RankerArgsInterface

from twon_lss.schemas import User, Post, Feed
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
    llm: LLM

    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        return random.uniform(0, 1)

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        return random.uniform(0, 1)
    

class LikeRanker(RankerInterface):
    llm: LLM

    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        return len(post.likes)

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:   
        return 0.0