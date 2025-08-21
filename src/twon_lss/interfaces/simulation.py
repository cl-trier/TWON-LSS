import abc
import typing
import logging
import pathlib
import json
import multiprocessing

import pydantic

from rich.progress import track

from twon_lss.interfaces import AgentInterface, RankerInterface
from twon_lss.schemas import User, Network, Feed, Post



class SimulationInterfaceArgs(pydantic.BaseModel):
    """
    TODO
    """

    num_steps: int = 100
    num_posts_to_interact_with: int = 5


class SimulationInterface(abc.ABC, pydantic.BaseModel):
    """
    TODO
    """

    args: SimulationInterfaceArgs = pydantic.Field(
        default_factory=SimulationInterfaceArgs
    )

    ranker: RankerInterface
    individuals: typing.Dict[User, AgentInterface]

    network: Network
    feed: Feed

    output_path: pydantic.DirectoryPath = pydantic.Field(
        default_factory=lambda: pathlib.Path.cwd() / "output/"
    )

    def model_post_init(self, __context: typing.Any):
        logging.debug(">f init simulation")
        self.output_path.mkdir(exist_ok=True)

    def __call__(self) -> None:
        """
        TODO
        """
        for n in track(range(self.args.num_steps)):
            logging.debug(f">f simulate step {n=}")
            self._step(n)

        self.network.to_json(self.output_path / "network.json")
        self.feed.to_json(self.output_path / "feed.json")
        self._individuals_to_json(self.output_path / "individuals.json")

    def _step(self, n: int = 0) -> None:
        """
        TODO
        """
        post_scores: typing.Dict[typing.Tuple[User, Post], float] = self.ranker(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )
        logging.debug(len(self.feed))
        logging.debug(len(post_scores.keys()))

        with multiprocessing.Pool() as pool:
            responses: typing.Tuple[User, AgentInterface, typing.List[Post]] = pool.starmap(
                self._wrapper_step_agent, 
                [
                    (post_scores, user, agent)
                    for user, agent in self.individuals.items()
                ]
            )
            
            self.individuals = {user: agent for user, agent, _ in responses}
            self.feed = Feed([post for _, _, agent_posts in responses for post in agent_posts])
            pool.close()
            pool.join()
    
    def _wrapper_step_agent(
            self, 
            post_scores: typing.Dict[typing.Tuple[User, Post], float],
            user: User, agent: AgentInterface
        ) -> typing.Tuple[User, AgentInterface]:
        user_feed = self._filter_posts_by_user(post_scores, user)
        user_feed.sort(key=lambda x: x[1], reverse=True)
        user_feed_top = user_feed[: self.args.num_posts_to_interact_with]

        logging.debug(f">i {len(user_feed)=}")

        return self._step_agent(user, agent, Feed([post for post, _ in user_feed_top]))

    @abc.abstractmethod
    def _step_agent(
        self, 
        user: User, 
        agent: AgentInterface, 
        feed: Feed
    ) -> typing.Tuple[User, AgentInterface, typing.List[Post]]:
        """
        TODO
        """
        pass

    def _individuals_to_json(self, path: str):
        json.dump(
            {
                user.id: agent.model_dump(mode="json", exclude=["llm"])
                for user, agent in self.individuals.items()
            },
            open(path, "w"),
            indent=4,
        )

    def _rankings_to_json(
        self, rankings: typing.Dict[typing.Tuple[User, Post], float], path: str
    ):
        json.dump(
            [
                {"user": user.id, "post": post.id, "score": score}
                for (user, post), score in rankings.items()
            ],
            open(path, "w"),
            indent=4,
        )

    @staticmethod
    def _filter_posts_by_user(
        posts_scores: typing.Dict[typing.Tuple[User, Post], float], user: User
    ) -> typing.List[typing.Tuple[Post, float]]:
        return [
            (post_content, post_score)
            for (post_user, post_content), post_score in posts_scores.items()
            if user == post_user
        ]
