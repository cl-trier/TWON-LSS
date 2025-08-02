import typing

import pydantic

if typing.TYPE_CHECKING:
    from twon_lss.agent import AgentInterface, AgentActions
    from twon_lss.ranking import RankingInterface

    from twon_lss.schemas import Feed, Network, User, Post


class SimulationArgs(pydantic.BaseModel):
    num_steps: int = 100
    num_posts_to_interact_with: int = 5


class Simulation(pydantic.BaseModel):
    args: "SimulationArgs"

    ranking: "RankingInterface"
    individuals: typing.Dict["User", "AgentInterface"]

    network: "Network"
    feed: "Feed"

    def __call__(self) -> None:
        pass

    def _step(self) -> None:
        post_scores: typing.Dict[("User", "Post"), float] = self.ranking(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )

        for i_user, i_agent in self.individuals.items():
            self._step_agent(
                i_agent,
                {
                    post: value
                    for (user, post), value in post_scores.items()
                    if user == i_user
                },
            )

    def _step_agent(self, agent: "AgentInterface", posts: typing.List["Post"]):
        for post in posts:
            actions = agent.select_actions(post)

            if AgentActions.post in actions:
                message = agent.post(post)
                print(message)

            if AgentActions.comment in actions:
                comment = agent.comment(post)
                print(comment)
