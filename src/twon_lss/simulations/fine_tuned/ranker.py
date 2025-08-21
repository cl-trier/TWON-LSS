import statistics

from twon_lss.interfaces import RankerInterface, RankerArgsInterface

from twon_lss.schemas import User, Post, Feed
from twon_lss.utility import LLM


__all__ = ["Ranker", "RankerArgs", "Engagement"]


class RankerArgs(RankerArgsInterface):
    pass

class Ranker(RankerInterface):
    llm: LLM

    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        return sum(len(post.likes))

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:
        return 1.0
        # FIXME authorization error on huggingface similarity endpoint
        return statistics.mean(
            self.llm.similarity(
                post.content, [item.content for item in feed.get_items_by_user(user)]
            )
        )
