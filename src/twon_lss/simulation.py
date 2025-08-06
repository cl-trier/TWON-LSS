import typing

import pydantic

from rich.progress import track

from twon_lss.agent import AgentInterface, AgentActions
from twon_lss.ranking import RankingInterface

from twon_lss.schemas import Feed, Network, User, Post, Interaction, InteractionTypes


class SimulationArgs(pydantic.BaseModel):
    num_steps: int = 100
    num_posts_to_interact_with: int = 5


class Simulation(pydantic.BaseModel):
    args: SimulationArgs

    ranking: RankingInterface
    individuals: typing.Dict[User, AgentInterface]

    network: Network
    feed: Feed

    def __call__(self) -> None:
        for _ in track(range(self.args.num_steps)):
            self._step()

    def _step(self) -> None:
        post_scores: typing.Dict[(User, Post), float] = self.ranking(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )

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

    def _step_agent(self, user: User, agent: AgentInterface, posts: Feed):
        print(user)

        for post in posts:
            actions = agent.select_actions(post)
            print(actions)

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
