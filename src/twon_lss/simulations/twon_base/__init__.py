import typing
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

    def _step(self) -> None:
        """
        TODO
        """
        post_scores: typing.Dict[(User, Post), float] = self.ranker(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )
        logging.debug(f">o global post scores | {post_scores}")

        for i_user, i_agent in self.individuals.items():
            # get user's post scores, sort by score, limit to top N
            user_feed: typing.List[(Post, float)] = [
                (post, score)
                for (user, post), score in post_scores.items()
                if user == i_user
            ]
            user_feed.sort(key=lambda x: x[1], reverse=True)
            user_feed_top = user_feed[: self.args.num_posts_to_interact_with]

            self._step_agent(i_user, i_agent, Feed([post for post, _ in user_feed_top]))

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
