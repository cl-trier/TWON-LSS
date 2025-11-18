from datetime import datetime
import argparse
import yaml
import json
import dotenv
import networkx
import random
from pathlib import Path
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
)

from twon_lss.schemas import Post, User, Feed, Network
from twon_lss.utility import LLM, Message, Chat, Noise



def load_config(config_path: str) -> argparse.Namespace:
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    return argparse.Namespace(**config_dict)

def simulation_main(args):
    
    # Set ENV
    ENV = dotenv.dotenv_values("../" * 3 + ".env")

    # Set seeds for reproducibility of user configuration || Attention: First simulation steps will remove seeds
    random.seed(args.seed)
    np.random.seed(args.seed)

    # Parameters
    LENGTH_AGENT_MEMORY: int = 10 # actions (20 prompt-completion pairs) => Past ~5 rounds (1 Feed Consumption + 1 Write)
    PERSISTENCE: int = args.persistence 
    STEPS: int = args.num_steps
    NUM_AGENTS: int = args.num_agents


    # Initialize ranker
    if args.ranker == "RandomRanker":
        RANKER = RandomRanker(
            args=RankerArgs(persistence=PERSISTENCE, noise=Noise(low=1.0, high=1.0))
        )
    elif args.ranker == "SemanticSimilarityRanker":
        RANKER = SemanticSimilarityRanker(
            llm=LLM(api_key=ENV["HF_TOKEN"], model="mxbai-embed-large-v1", url="https://router.huggingface.co/hf-inference/models/mixedbread-ai/mxbai-embed-large-v1/pipeline/feature-extraction"),
            args=RankerArgs(persistence=PERSISTENCE, noise=Noise(low=1.0, high=1.0))
        )


    # Load LLM
    AGENT_LLM = WP3LLM(
        api_key=ENV["RUNPOD_TOKEN"],
        url=args.runpod_url,
    )


    # Set up agents and users and individuals
    # Agents
    AGENTS_INSTRUCTIONS_CFG = json.load(open("../data/agents.instructions.json"))
    AGENTS_PERSONAS_CFG = json.load(open("../data/agents.personas.json"))
    AGENTS_PERSONAS_CFG = random.sample(AGENTS_PERSONAS_CFG, k=NUM_AGENTS)
    AGENTS_PERSONAS_CFG = sorted(AGENTS_PERSONAS_CFG, key=lambda x: x["posts_per_day"], reverse=True)

    # Users
    usernames = [user.get("screen_name", f"User{i}") for i, user in enumerate(AGENTS_PERSONAS_CFG)]    
    USERS = [User(id=username) for username in usernames]

    # Individuals
    INDIVIDUALS = {
        user: WP3Agent(
            llm=AGENT_LLM,
            instructions=AgentInstructions(**AGENTS_INSTRUCTIONS_CFG["actions"]),
            cognition=persona["cognition"],
            bio=persona["bio"],
            memory=persona["history"][-LENGTH_AGENT_MEMORY*2:],
            memory_length=LENGTH_AGENT_MEMORY,
            activation_probability=agent_parameter_estimation(posts_per_day=persona["posts_per_day"], seed=i)["activation_probability"],
            posting_probability=agent_parameter_estimation(posts_per_day=persona["posts_per_day"], seed=i)["posting_probability"],
            read_amount=agent_parameter_estimation(posts_per_day=persona["posts_per_day"], seed=i)["read_amount"],
        )
        for i, (user, persona) in enumerate(zip(
            USERS, AGENTS_PERSONAS_CFG, strict=False
        ))
    }


    # Set up network
    if args.network_type == "complete":
        NETWORK = Network.from_graph(networkx.complete_graph(n = len(USERS)), USERS)
    elif args.network_type == "barabasi_albert":
        NETWORK = Network.from_graph(networkx.barabasi_albert_graph(n = len(USERS), m=args.m), USERS)



    # Set up initial feed
    init_tweets = [
        [message.get("content") for message in personas["history"] if message.get("role") == "assistant"]
        for personas in AGENTS_PERSONAS_CFG
    ]
    FEED = Feed([
        Post(user=user, content=post)
        for user, history in zip(USERS, init_tweets, strict=False)
        for post in history[-2:]
    ])

    
    # Initialize simulation
    simulation = Simulation(
        args=SimulationArgs(num_steps=STEPS),
        ranker=RANKER,
        individuals=INDIVIDUALS,
        network=NETWORK,
        feed=FEED,
        output_path=Path(f"runs/{args.model_name}-{args.num_agents}-{args.network_type}-Seed{args.seed}-{args.ranker}-{datetime.now().strftime('%Y%m%d_%H%M%S')}/").mkdir(exist_ok=True, parents=True) or f"runs/{args.model_name}-{args.num_agents}-{args.network_type}-Seed{args.seed}-{args.ranker}-{datetime.now().strftime('%Y%m%d_%H%M%S')}/"
    )
    
    # Save configuration
    with open(Path(simulation.output_path) / "simulation_config.yaml", "w") as f:
        args.version = "1.0.1" # Increase if script changes!!!
        yaml.dump(vars(args), f)

    # Start simulation
    simulation()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config file to override arguments")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--num_agents", type=int, default=1028, help="Number of agents in the simulation")
    parser.add_argument("--num_steps", type=int, default=288, help="Number of simulation steps")
    parser.add_argument("--network_type", type=str, default="complete", help="Type of network to use (e.g., complete, barabasi_albert)")
    parser.add_argument("--m", type=int, default=40, help="Barabasi-Albert model parameter m (number of edges to attach from a new node to existing nodes)")
    parser.add_argument("--persistence", type=int, default=144, help="Ranker persistence in steps")
    parser.add_argument("--ranker", type=str, default="RandomRanker", help="Type of ranker to use (e.g., RandomRanker, SemanticSimilarityRanker)")
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--runpod_url", type=str)
    args = parser.parse_args()

    # Override with YAML if provided
    if args.config:
        yaml_args = load_config(args.config)
        # Merge: CLI args override YAML
        for key, value in vars(yaml_args).items():
            if not hasattr(args, key) or getattr(args, key) == parser.get_default(key):
                setattr(args, key, value)
    
    simulation_main(args)