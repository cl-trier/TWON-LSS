import abc

import pydantic


class AgentArgsInterface(abc.ABC, pydantic.BaseModel):
    pass


class AgentInterface(abc.ABC, pydantic.BaseModel):
    args: AgentArgsInterface = AgentArgsInterface()


# NOTE attribute initial_action_likelihoods to map influencer and bystander agents
