import typing

from twon_lss.interfaces import (
    AgentInterface,
    AgentActions,
    SimulationInterface,
    SimulationInterfaceArgs,
)
from twon_lss.schemas import Feed, User, Post


from twon_lss.simulations.bcm.agent import Agent
from twon_lss.simulations.bcm.ranker import Ranker, RankerArgs


__all__ = [
    "Simulation",
    "SimulationArgs",
    "Agent",
    "AgentInstructions",
    "Ranker",
    "RankerArgs",
]


class SimulationArgs(SimulationInterfaceArgs):
    pass


class Simulation(SimulationInterface):

    def _step_agent(self, user: User, agent: AgentInterface, feed: Feed):
        new_posts: typing.List[Post] = []

        for post in feed:
            actions = agent.select_actions(post)

            if AgentActions.post in actions:
                new_posts.append(Post(user=user, content=agent.post(post)))

        return user, agent, new_posts
