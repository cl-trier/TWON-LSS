import logging
import multiprocessing
import typing
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import random

from twon_lss.interfaces import (
    AgentInterface,
    AgentActions,
    SimulationInterface,
    SimulationInterfaceArgs,
)
from twon_lss.schemas import Feed, User, Post


from twon_lss.simulations.wp3_simulation.agent import WP3Agent, AgentInstructions
from twon_lss.simulations.twon_base.ranker import Ranker, RankerArgs, RandomRanker, LikeRanker, UserLikeRanker, PersonalizedUserLikeRanker, SemanticSimilarityRanker

from twon_lss.simulations.wp3_simulation.utility import WP3LLM


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
    "SemanticSimilarityRanker",
    "RankerArgs",
    "WP3LLM",
]


class SimulationArgs(SimulationInterfaceArgs):
    num_steps: int = 100


class Simulation(SimulationInterface):

    def model_post_init(self, __context: typing.Any):
        
        if hasattr(self.ranker, "llm") and self.ranker.llm is not None:
            logging.debug(f">f generating embeddings for {len(self.feed)} feed posts")
            embeddings = self.ranker.llm.extract(
                [post.content for post in self.feed]
            )
            for post, embedding in zip(self.feed, embeddings):
                post.embedding = embedding

        logging.debug(">f init simulation")
        self.output_path.mkdir(exist_ok=True)


    def _wrapper_step_agent(
        self,
        post_scores: typing.Dict[typing.Tuple[User, Post], float],
        user: User,
        agent: AgentInterface,
    ) -> typing.Tuple[User, AgentInterface]:
        user_feed = self._filter_posts_by_user(post_scores, user)
        user_feed.sort(key=lambda x: x[1], reverse=True)
        

        ### UPDATED FOR WP3 MODEL ###
        # Determine how many posts the users reads
        read_count : int = agent.theta * 10 # PLACEHOLDER
        user_feed_top = user_feed[: int(read_count)]

        logging.debug(f">i number of feed items {len(user_feed)} for user {user.id}")
        return self._step_agent(user, agent, Feed([post for post, _ in user_feed_top]))


    ### UPDATED FOR WP3 MODEL ###
    def _step_agent(self, user: User, agent: WP3Agent, feed: Feed):
        posts: typing.List[Post] = []

        if random.random() > agent.theta: # PLACEHOLDER
            return user, agent, posts # Session not activated

        ### Session activated
        agent.activations += 1
        # Read posts in the feed
        for post in feed:
            post.reads.append(user)
        agent.read_and_like(feed, user)

        # Post new posts
        post_probability = agent.theta * 2 # PLACEHOLDER
        while post_probability >= 1.0:
            posts.append(Post(user=user, content=agent.post()))
            post_probability = post_probability - 1.0
        if post_probability > 0 and post_probability > random.random():
            posts.append(Post(user=user, content=agent.post()))

        # Update cognition
        if agent.activations % 3 == 0:  # PLACEHOLDER
            agent.cognition_update()

        return user, agent, posts
    

    def _step(self, n: int = 0) -> None:
        post_scores: typing.Dict[typing.Tuple[User, Post], float] = self.ranker(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )

        # For I/O bound: more workers; for CPU bound: stick to cpu_count
        max_workers = min(len(self.individuals), multiprocessing.cpu_count() * 2)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._wrapper_step_agent, post_scores, user, agent): user 
                for user, agent in self.individuals.items()
            }
            
            responses = []
            for future in as_completed(futures):
                responses.append(future.result())


        # Add ID to posts
        posts = [post for _, _, agent_posts in responses for post in agent_posts]
        for post in posts:
            post.timestamp = n

        # Generate embeddings if required
        if hasattr(self.ranker, "llm") and self.ranker.llm is not None:
            logging.debug(f">f generating embeddings for {len(posts)} posts")
            embeddings = self.ranker.llm.extract([post.content for post in posts])

            for post, embedding in zip(posts, embeddings):
                post.embedding = embedding


        self.individuals = {user: agent for user, agent, _ in list(responses)}
        self.feed.extend(posts)