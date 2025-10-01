import json
import logging
import rich
import dotenv
import networkx
import random
from pathlib import Path
import typing


from twon_lss.simulations.twon_base import (
    Simulation,
    SimulationArgs,
    Ranker,
    RandomRanker,
    LikeRanker,
    UserLikeRanker,
    PersonalizedUserLikeRanker,
    SemanticSimilarityRanker,
    RankerArgs,
    Agent,
    AgentInstructions,
)

from twon_lss.schemas import Post, User, Feed, Network
from twon_lss.utility import LLM, Message



# Fixed across experiments
LENGTH_AGENT_MEMORY: int = 21 # actions (42 prompt-completion pairs) => 7 rounds a 2 reads and 1 write
PERSISTENCE: int = 4
NUM_POSTS_TO_INTERACT_WITH: int = 2
STEPS: int = 50

# Varies across experiments
NUM_AGENTS: int = 128

# Fix seed
random.seed(42)

ENV = dotenv.dotenv_values("../" * 2 + ".env")
AGENTS_INSTRUCTIONS_CFG = json.load(open("./data/agents.instructions.json"))
AGENTS_PERSONAS_CFG = json.load(open("./data/agents.personas.json"))
AGENTS_PERSONAS_CFG = random.sample(AGENTS_PERSONAS_CFG, k=NUM_AGENTS)



# Rankers to test
RANKERS: typing.List[typing.Type[Ranker]] = [
    SemanticSimilarityRanker(
        llm=LLM(api_key=ENV["HF_TOKEN"], model="mxbai-embed-large-v1", url="https://router.huggingface.co/hf-inference/models/mixedbread-ai/mxbai-embed-large-v1/pipeline/feature-extraction"),
        args=RankerArgs(persistence=PERSISTENCE)
    )
]
RANKER_NAMES = ["SemanticSimilarityRanker"]




AGENT_LLM = LLM(api_key=ENV["HF_TOKEN"], model="meta-llama/Llama-3.1-8B-Instruct:cerebras")



usernames = [LLM.generate_username(AGENT_LLM, history.get("messages", [])) for history in AGENTS_PERSONAS_CFG]


histories = [
    [message.get("content") for message in personas["messages"] if message.get("role") == "assistant"]
    for personas in AGENTS_PERSONAS_CFG
]


for ranker_implementation, ranker_name in zip(RANKERS, RANKER_NAMES):

    print(f"Starting simulation with {ranker_name}...")

    USERS = [User(id=username) for username in usernames]

    NETWORK = Network.from_graph(networkx.watts_strogatz_graph(n=len(USERS), k=14, p=0.05, seed=42), USERS)

    FEED = Feed(
    [
        Post(user=user, content=post)
        for user, history in zip(USERS, histories, strict=False)
        for post in history[:2]
    ]
    )

    INDIVIDUALS = {
        user: Agent(
            llm=AGENT_LLM,
            instructions=AgentInstructions(
                persona=AGENTS_INSTRUCTIONS_CFG["persona"], **AGENTS_INSTRUCTIONS_CFG["actions"]
            ),
            memory=history["messages"][1:LENGTH_AGENT_MEMORY*2 + 1],
            memory_length=LENGTH_AGENT_MEMORY
        )
        for user, history in zip(
            USERS, AGENTS_PERSONAS_CFG, strict=False
        )
    }

    simulation = Simulation(
        args=SimulationArgs(num_steps=STEPS, num_posts_to_interact_with=NUM_POSTS_TO_INTERACT_WITH),
        ranker=ranker_implementation,
        individuals=INDIVIDUALS,
        network=NETWORK,
        feed=FEED,
        output_path=Path(f"Output_128agents_WattsStrogatz/{ranker_name}/").mkdir(exist_ok=True, parents=True) or f"Output_128agents_WattsStrogatz/{ranker_name}/"
    )

    simulation()