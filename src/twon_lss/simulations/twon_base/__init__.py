import logging

from twon_lss.interfaces import (
    AgentInterface,
    AgentActions,
    SimulationInterface,
    SimulationInterfaceArgs,
)
from twon_lss.schemas import Feed, User, Post, Interaction, InteractionTypes


from twon_lss.simulations.twon_base.agent import Agent, AgentInstructions
from twon_lss.simulations.twon_base.ranker import Ranker, RankerArgs


__all__ = [
    "Simulation",
    "SimulationArgs",
    "Agent",
    "AgentInstructions",
    "Ranker",
    "RankerArgs",
]


class SimulationArgs(SimulationInterfaceArgs):
    """
    TODO
    """

    pass


class Simulation(SimulationInterface):
    """
    TODO
    """

    def _step_agent(self, user: User, agent: AgentInterface, feed: Feed):
        """
        TODO
        """
        logging.debug(f">f perform agent simulation step | {user.id=}")
        logging.debug(f">i selected feed for agent | {feed}")

        for post in feed:
            actions = agent.select_actions(post)
            logging.debug(f">o selected actions for post | {post.id=} {actions=}")

            if actions:
                if InteractionTypes.read in actions:
                    post.interactions.append(
                        Interaction(user=user, type=InteractionTypes.read)
                    )

                if AgentActions.like in actions:
                    post.interactions.append(
                        Interaction(user=user, type=InteractionTypes.like)
                    )

                if AgentActions.post in actions:
                    content = agent.post(post)

                    new_post = Post(user=user, content=content)
                    self.feed.root.append(new_post)

                if AgentActions.comment in actions:
                    content = agent.comment(post)

                    new_comment = Post(
                        user=user,
                        content=content,
                    )

                    post.add_comment(new_comment)
