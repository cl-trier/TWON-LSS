import typing

from twon_lss.interfaces import (
    AgentInterface,
    AgentActions,
    SimulationInterface,
    SimulationInterfaceArgs,
)
from twon_lss.schemas import Feed, User, Post


from twon_lss.simulations.twon_base.agent import Agent, AgentInstructions
from twon_lss.simulations.twon_base.ranker import Ranker, RankerArgs, RandomRanker, LikeRanker, UserLikeRanker, PersonalizedUserLikeRanker


__all__ = [
    "Simulation",
    "SimulationArgs",
    "Agent",
    "AgentInstructions",
    "Ranker",
    "RandomRanker",
    "LikeRanker",
    "UserLikeRanker",
    "PersonalizedUserLikeRanker",
    "RankerArgs",
]


class SimulationArgs(SimulationInterfaceArgs):
    pass


class Simulation(SimulationInterface):
    def _step_agent(self, user: User, agent: Agent, feed: Feed):
        new_posts: typing.List[Post] = []

        for post in feed:
            post.reads.append(user)
            
            if agent.consume_and_rate(post):
                post.likes.append(user)

        # Post after reading the feed
        new_posts.append(Post(user=user, content=agent.post()))

        return user, agent, new_posts
