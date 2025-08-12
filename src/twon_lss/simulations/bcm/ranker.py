import typing
import random

from twon_lss.interfaces import RankerInterface, RankerArgsInterface

from twon_lss.schemas import User, Post, Feed


__all__ = ["Ranker", "RankerArgs", "Engagement"]



class RankerArgs(RankerArgsInterface):
    pass

class Ranker(RankerInterface):
    type: typing.Optional[typing.Literal["random", "positivity", "negativity"]] = "random"
    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        if self.type == "random":
            return random.uniform(-1.0, 1.0)
        
        elif self.type == "positivity":
            return float(post.content)
        
        elif self.type == "negativity":
            return float(post.content) * -1
        
        else:
            return 0.0

    def _compute_individual(self, user: User, _p: Post, _f: Feed) -> float:
        return 0.0
       
