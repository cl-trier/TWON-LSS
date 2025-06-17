import abc
import typing

import pydantic

from twon_lss.schemas import Post


class RankingArgsInterface(abc.ABC, pydantic.BaseModel):
    pass


class RankingInterface(abc.ABC, pydantic.BaseModel):
    args: RankingArgsInterface = RankingArgsInterface()

    def __call__(self, posts: typing.List["Post"]) -> typing.Dict[str, float]:
        return {post.id: self._compute_post_score(post) for post in posts}

    @abc.abstractmethod
    def _compute_post_score(self, post: "Post") -> float:
        pass
