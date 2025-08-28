import logging
import multiprocessing
import typing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing

from twon_lss.interfaces import (
    AgentInterface,
    AgentActions,
    SimulationInterface,
    SimulationInterfaceArgs,
)
from twon_lss.schemas import Feed, User, Post


from twon_lss.simulations.twon_base.agent import Agent, AgentInstructions
from twon_lss.simulations.twon_base.ranker import Ranker, RankerArgs, RandomRanker, LikeRanker, UserLikeRanker, PersonalizedUserLikeRanker, SemanticSimilarityRanker


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
]


class SimulationArgs(SimulationInterfaceArgs):
    pass


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


    def _step_agent(self, user: User, agent: Agent, feed: Feed):
        new_posts: typing.List[Post] = []

        for post in feed:
            post.reads.append(user)
            
            if agent.consume_and_rate(post):
                post.likes.append(user)

        # Post after reading the feed
        new_posts.append(Post(user=user, content=agent.post()))

        return user, agent, new_posts
    


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
