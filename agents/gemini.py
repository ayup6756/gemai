import time
from google import genai
from google.genai import types
from config.config import Config
from models.agent_config import AgentConfig
from models.agent import Agent, AgentOutput, MasterAgent, WorkerAgent


class GeminiFlash(MasterAgent):
    def __init__(self, agent_config: AgentConfig):
        self.client = genai.Client(api_key=agent_config.api_key)
        self.agent_config = agent_config
        self.agents: dict[str, Agent] = {}
        self.main_prompt = agent_config.main_prompt

        self.contents: list[types.Content] = []

    def add_user_history(self, text: str):
        self.contents.append(types.UserContent(parts=[types.Part.from_text(text=text)]))

    def add_model_history(self, content: types.Content):
        self.contents.append(content)

    def add_worker_agent(self, worker_agent: Agent):
        self.agents[worker_agent.agent_config.agent_id] = worker_agent
        # if first agent
        if len(self.agents) == 1:
            self.main_prompt += "\n"
            self.main_prompt += Config.agent_info_prompt

        self.main_prompt += "\n"
        self.main_prompt += f"{worker_agent.agent_config.agent_id} - {worker_agent.agent_config.description}"

    def generate_response(self, text: str) -> AgentOutput:
        if len(self.contents) == 0:
            self.contents.append(
                types.UserContent(parts=[types.Part.from_text(text=self.main_prompt)])
            )

        if self.agent_config.save_history:
            self.add_user_history(text)
        else:
            self.contents = [
                self.contents[0],
                types.UserContent(parts=[types.Part.from_text(text=text)]),
            ]

        try:
            start = time.time()

            resp = self.client.models.generate_content(
                model=self.agent_config.model_name,
                contents=self.contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                ),
            )

            end = time.time()

            content = resp.candidates[0].content
            if self.agent_config.save_history:
                self.add_model_history(content=content)

            return AgentOutput(content=content, duration=end - start)
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

class GeminiImage(WorkerAgent):
    def __init__(self, agent_config: AgentConfig):
        self.client = genai.Client(api_key=agent_config.api_key)
        self.agent_config = agent_config

        self.contents: list[types.Content] = []

    def add_user_history(self, text: str):
        self.contents.append(types.UserContent(parts=[types.Part.from_text(text=text)]))

    def add_model_history(self, content: types.Content):
        self.contents.append(content)

    def generate_response(self, text: str) -> AgentOutput:
        if self.agent_config.save_history:
            self.add_user_history(text)
        else:
            self.contents = [
                types.UserContent(
                    parts=[types.Part.from_text(text=self.agent_config.main_prompt)]
                ),
                types.UserContent(parts=[types.Part.from_text(text=text)]),
            ]

        try:
            start = time.time()

            resp = self.client.models.generate_content(
                model=self.agent_config.model_name,
                contents=self.contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                ),
            )

            end = time.time()

            content = resp.candidates[0].content
            if self.agent_config.save_history:
                self.add_model_history(content=content)

            return AgentOutput(content=content, duration=end - start)
        except Exception as e:
            print(f"Error generating content: {e}")
            return None
