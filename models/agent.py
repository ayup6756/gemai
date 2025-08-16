from abc import ABC, abstractmethod
from google.genai import types
from pydantic import BaseModel
from models.agent_config import AgentConfig



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


class AgentCall(BaseModel):
    name: str = None
    query: str = None

class WorkerAgent(Agent):
    pass

class MasterAgent(Agent):
    @abstractmethod
    def add_worker_agent(self, worker_agent: Agent):
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




