from abc import ABC, abstractmethod
from typing import Union
from google.genai import types
from pydantic import BaseModel
from models.agent_config import AgentConfig

class AgentCall(BaseModel):
    name: str = None
    query: str = None

class ToolCall(BaseModel):
    name: str = None
    query: dict = None


class AgentTool(ABC):

    description: str
    tool_id: str

    @abstractmethod
    def __init__(self, description: str, input_fields_description: dict, tool_id: str):
        pass

    @abstractmethod
    def run(self, query: dict) -> str:
        pass

    def __str__(self):
        out = f"{self.tool_id} - {self.description}"

        for key in self.input_fields_description.keys():
            out += "\n"
            out += "  queries:\n"
            out += f"    {key} - {self.input_fields_description[key]}"

        return out

class AgentOutput(BaseModel):
    content: types.Content
    duration: float


class Agent(ABC):
    
    agent_config: AgentConfig

    @abstractmethod
    def add_user_history(self, text: str):
        pass

    @abstractmethod
    def add_model_history(self, content: types.Content):
        pass

    @abstractmethod
    def generate_response(self, text: str) -> AgentOutput:
        pass

    @abstractmethod
    def process_output(self, output: AgentOutput) -> types.Content:
        pass

    @abstractmethod
    def run(self, text: str) -> types.Content:
        pass

    def __str__(self):
        return f"{self.agent_config.agent_id} - {self.agent_config.description}"


class WorkerAgent(Agent):
    pass


class MasterAgent(Agent):

    @abstractmethod
    def add_worker_agent(self, worker_agent: Agent):
        pass

    @abstractmethod
    def add_tool(self, tool: AgentTool):
        pass

    @abstractmethod
    def add_user_content_history(self, content: types.Content):
        pass

    @abstractmethod
    def add_model_text_history(self, text: str):
        pass

    @abstractmethod
    def process_output(self, output: AgentOutput) -> AgentCall:
        pass




