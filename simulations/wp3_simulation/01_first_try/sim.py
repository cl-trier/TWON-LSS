import json
import logging
import dotenv
import networkx
import random
from pathlib import Path
import typing
import numpy as np

from twon_lss.simulations.wp3_simulation import (
    RandomRanker,
    SemanticSimilarityRanker,
    RankerArgs,
)

from twon_lss.simulations.wp3_simulation import (
    Simulation,
    SimulationArgs,
    WP3Agent,
    AgentInstructions,
    WP3LLM,
    agent_parameter_estimation,
    simulation_load_estimator,
)

from twon_lss.schemas import Post, User, Feed, Network
from twon_lss.utility import LLM, Message, Chat, Noise

import time
import argparse

# Set up argument parser for seed
parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=42, help="Random seed")
args = parser.parse_args()

# Set seeds for reproducibility of user configuration || Attention: First simulation steps will remove seeds
random.seed(args.seed)
np.random.seed(args.seed)

# Fixed across experiments
LENGTH_AGENT_MEMORY: int = 10 # actions (20 prompt-completion pairs) => Past ~5 rounds (1 Feed Consumption + 1 Write)
PERSISTENCE: int = 288 # Full 2 days
STEPS: int = 288 # 2 days

# Varies across experiments
NUM_AGENTS: int = 512


ENV = dotenv.dotenv_values("../" * 3 + ".env")
AGENTS_INSTRUCTIONS_CFG = json.load(open("../data/agents.instructions.json"))
AGENTS_PERSONAS_CFG = json.load(open("../data/agents.personas_dummy.json"))
AGENTS_PERSONAS_CFG = random.sample(AGENTS_PERSONAS_CFG, k=NUM_AGENTS)


# Load estimator config
simulation_load_estimator([agent_parameter_estimation(posts_per_day = agent["posts_per_day"], seed=i) for i, agent in enumerate(AGENTS_PERSONAS_CFG)], user_confirmation=True)

# Rankers to test
RANKERS = [
    RandomRanker(
        args=RankerArgs(persistence=PERSISTENCE, noise=Noise(low=1.0, high=1.0))
    ),
    SemanticSimilarityRanker(
        llm=LLM(api_key=ENV["HF_TOKEN"], model="mxbai-embed-large-v1", url="https://router.huggingface.co/hf-inference/models/mixedbread-ai/mxbai-embed-large-v1/pipeline/feature-extraction"),
        args=RankerArgs(persistence=PERSISTENCE, noise=Noise(low=1.0, high=1.0))
    )
]
RANKER_NAMES = ["RandomRanker", "SemanticSimilarityRanker"]

AGENT_LLM = WP3LLM(
    api_key=ENV["RUNPOD_TOKEN"],
    url="https://api.runpod.ai/v2/coviy771dq84f3/runsync"
)

usernames = [user.get("screen_name", f"User{i}") for i, user in enumerate(AGENTS_PERSONAS_CFG)]

init_tweets = [
    [message.get("content") for message in personas["history"] if message.get("role") == "assistant"]
    for personas in AGENTS_PERSONAS_CFG
]

for ranker_implementation, ranker_name in zip(RANKERS, RANKER_NAMES):

    USERS = [User(id=username) for username in usernames]

    NETWORK = Network.from_graph(networkx.complete_graph(n = len(USERS)), USERS)

    FEED = Feed([
        Post(user=user, content=post)
        for user, history in zip(USERS, init_tweets, strict=False)
        for post in history[-2:]
    ])
    
    INDIVIDUALS = {
        user: WP3Agent(
            llm=AGENT_LLM,
            instructions=AgentInstructions(**AGENTS_INSTRUCTIONS_CFG["actions"]),
            cognition=persona["cognition"],
            bio=persona["bio"],
            memory=persona["history"],
            memory_length=LENGTH_AGENT_MEMORY,
            activation_probability=agent_parameter_estimation(posts_per_day=persona["posts_per_day"], seed=i)["activation_probability"],
            posting_probability=agent_parameter_estimation(posts_per_day=persona["posts_per_day"], seed=i)["posting_probability"],
            read_amount=agent_parameter_estimation(posts_per_day=persona["posts_per_day"], seed=i)["read_amount"],
        )
        for i, (user, persona) in enumerate(zip(
            USERS, AGENTS_PERSONAS_CFG, strict=False
        ))
    }

    simulation = Simulation(
        args=SimulationArgs(num_steps=STEPS),
        ranker=ranker_implementation,
        individuals=INDIVIDUALS,
        network=NETWORK,
        feed=FEED,
        output_path=Path(f"Qwen3-8B-512-FullyConnected-Seed{args.seed}/{ranker_name}/").mkdir(exist_ok=True, parents=True) or f"Qwen3-8B-512-FullyConnected-Seed{args.seed}/{ranker_name}/"
    )
    simulation()