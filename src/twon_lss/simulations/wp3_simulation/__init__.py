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
from twon_lss.simulations.wp3_simulation.ranker import RankerArgs, SemanticSimilarityRanker

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

        # add posts to agents
        for post in self.feed:
            agent = self.individuals.get(post.user)
            if agent:
                agent.posts.append(post)

        logging.debug(">f init simulation")
        self.output_path.mkdir(exist_ok=True)


    def _wrapper_step_agent(
        self,
        post_scores: typing.Dict[typing.Tuple[User, Post], float],
        user: User,
        agent: AgentInterface,
    ):
        user_feed = self._filter_posts_by_user(post_scores, user)
        user_feed.sort(key=lambda x: x[1], reverse=True)

        return self._step_agent(user, agent, Feed([post for post, _ in user_feed]))


    def _step_agent(self, user: User, agent: WP3Agent, feed: Feed):

        posts: typing.List[Post] = []

        # Determine how many posts the users reads
        user_feed_top = feed[:int(max(agent.theta * 100, 10))] # PLACEHOLDER
        logging.debug(f">i number of feed items {len(user_feed_top)} for user {user.id}")

        # Determine if the user activates this session
        if random.random() > agent.theta: # PLACEHOLDER
            return user, agent, posts # Session not activated

        # Session activates
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
            agent.posts.append
        if post_probability > 0 and post_probability > random.random():
            posts.append(Post(user=user, content=agent.post()))

        agent.posts.extend(posts)

        # Update cognition
        if agent.activations % 3 == 0:  # PLACEHOLDER
            agent.cognition_update()

        return user, agent, posts
    

    def _step(self, n: int = 0) -> None:
        # Strip feed to only recent posts for efficiency
        stripped_feed = self.feed.filter_by_timestamp(n, self.ranker.args.persistence)
        
        # Calculate post scores
        post_scores: typing.Dict[typing.Tuple[User, Post], float] = self.ranker(
            individuals=self.individuals, feed=stripped_feed, network=self.network
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

        # Add timestamp to posts
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