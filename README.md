# TWON - Large Scale Simulation (LSS)

A modular, scalable framework for simulating large-scale social media interactions and discourse dynamics. TWON-LSS enables researchers to model agent behavior, content propagation, and network effects in social platforms.

## Features

- Lightweight, API-driven architecture: Custom component integration with third-party service connections
- Modular design: Easy customization of network mechanics, agent models, and evaluation pipelines
- Multiple simulation types: Built-in BCM (Bounded Confidence Model) and TWON-base simulations
- LLM integration: Support for language model-powered agents with configurable instructions

## Architecture

### Network Mechanics

- Content ranking and recommendation algorithms
- Feed/discourse structure management (linear, tree-like)
- Message and notification routing system
- Platform-specific behaviors (e.g., Twitter-like vs. Reddit-like)

### Agent (User) Modeling

- User behavior and lifecycle simulation
- Interaction scheduling and patterns
- Content consumption and engagement logic
- LLM API integration for content generation

### Discourse Evaluation

- Count-based aggregation tools
- Automated content classification
- Analysis pipeline integration
- Results compilation and export

## Project Structure
```
twon_lss/
├── interfaces/           # Abstract base classes
│   ├── agent.py         # Agent behavior interface
│   ├── ranker.py        # Content ranking interface
│   └── simulation.py    # Simulation orchestration
├── schemas/             # Core data models
│   ├── user.py         # User representation
│   ├── post.py         # Post and interaction data
│   ├── feed.py         # Content aggregation
│   └── network.py      # Social network structure
├── simulations/         # Implemented simulation types
│   ├── bcm/            # Bounded Confidence Model
│   └── twon_base/      # LLM-powered social simulation
└── utility/            # Supporting utilities
    ├── llm.py          # Language model integration
    └── noise.py        # Randomization utilities
```

## Core Components

### Network Mechanics (`src/twon_lss/schemas/network.py`)
- NetworkX-based graph structures for user connections
- Neighbor discovery and relationship management
- JSON serialization for analysis and visualization

### Agent Modeling (`src/twon_lss/interfaces/agent.py`)
- Abstract agent interface with action selection and content generation
- Support for reading, liking, and posting behaviors
- Memory management and interaction patterns

### Content Ranking (`src/twon_lss/interfaces/ranker.py`)
- Configurable ranking algorithms combining network and individual scores
- Noise injection for realistic variability
- Extensible scoring mechanisms

### Feed Management (`src/twon_lss/schemas/feed.py`)
- Post aggregation and filtering by user
- Read/unread state tracking
- Content timeline management

### Simulation Engine (`src/twon_lss/interfaces/simulation.py`)
- Step-by-step simulation execution with progress tracking
- Automatic result export and serialization
- Configurable interaction limits and parameters

## Output Files
After running a simulation, the following files are generated:

- `network.json`: Social network structure and connections
- `feed.json`: Complete post history and interactions
- `individuals.json`: Final agent states and configurations

## Available Simulations

### BCM (Bounded Confidence Model)
A mathematical model simulating opinion dynamics where agents adjust their opinions based on similar others within a confidence threshold.

**Features:**

- Epsilon-delta opinion updating mechanism
- Configurable confidence bounds
- Memory-based opinion tracking

## TWON-Base
A comprehensive social media simulation with LLM-powered agents that can read, evaluate, and generate content.

**Features:**

- Persona-driven agent behavior
- Content consumption and rating
- Dynamic post generation
- Similarity-based content ranking

## Related Projects

- OASIS: Open Agents Social Interaction Simulations on One Million Agents <https://oasis.camel-ai.org>
