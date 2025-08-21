import abc
import typing
import logging
import pathlib
import json
import multiprocessing
import itertools, functools

import pydantic

from rich.progress import track

from twon_lss.interfaces import AgentInterface, RankerInterface, RankerScores
from twon_lss.schemas import User, Network, Feed, Post, PostID


class SimulationInterfaceArgs(pydantic.BaseModel):
    num_steps: int = 100
    num_posts_to_interact_with: int = 5


class SimulationInterface(abc.ABC, pydantic.BaseModel):
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

    def model_post_init(self, _: typing.Any):
        logging.debug(">f init simulation")
        self.output_path.mkdir(exist_ok=True)

    def __call__(self) -> None:
        for n in track(range(self.args.num_steps)):
            logging.debug(f">f simulate step {n=}")
            self._step(n)

        self.network.to_json(self.output_path / "network.json")
        self.feed.to_json(self.output_path / "feed.json")
        self._individuals_to_json(self.output_path / "individuals.json")

    def _step(self, n: int = 0) -> None:
        post_scores: RankerScores = self.ranker(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )
        logging.debug(f">i number of feed items {len(self.feed)}")

        # with multiprocessing.Pool() as pool:
        responses: typing.List[typing.Tuple[User, AgentInterface, typing.List[Post]]] = list(
            itertools.starmap(
                self._wrapper_step_agent, 
                [(post_scores, user, agent) for user, agent in self.individuals.items()]
            )
        )
        self.individuals = {user: agent for user, agent, _ in list(responses)}
        self.feed.extend([post for _, _, agent_posts in responses for post in agent_posts])

    def _wrapper_step_agent(
            self, 
            post_scores: RankerScores,
            user: User, agent: AgentInterface
        ) -> typing.Tuple[User, AgentInterface]:
        user_feed = post_scores.filter_by_user(user)
        user_feed.sort(key=lambda x: x[1], reverse=True)
        user_feed_top = user_feed[: self.args.num_posts_to_interact_with]

        logging.debug(f">i number of feed items {len(user_feed)} for user {user.id}")
        return self._step_agent(user, agent, Feed([self.feed.get_item_by_id(post_id) for post_id, _ in user_feed_top]))

    @abc.abstractmethod
    def _step_agent(
        self, 
        user: User, 
        agent: AgentInterface, 
        feed: Feed
    ) -> typing.Tuple[User, AgentInterface, typing.List[Post]]:
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
