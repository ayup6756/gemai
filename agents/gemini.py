import time
from google import genai
from google.genai import types
from config.config import Config
from models.agent_config import AgentConfig
from models.agent import Agent, AgentCall, AgentOutput, MasterAgent, WorkerAgent
from utils.agent_call import identify_agent_call
from utils.display import TerminalDisplay


class GeminiFlash(MasterAgent):
    def __init__(self, agent_config: AgentConfig):
        self.client = genai.Client(api_key=agent_config.api_key)
        self.agent_config = agent_config
        self.agents: dict[str, Agent] = {}
        self.main_prompt = agent_config.main_prompt
        self.term_display = TerminalDisplay()

        self.contents: list[types.Content] = []

    def add_user_history(self, text: str):
        self.contents.append(types.UserContent(parts=[types.Part.from_text(text=text)]))

    def add_user_content_history(self, content: types.Content):
        content.role = "user"
        self.contents.append(content)

    def add_model_text_history(self, text: str):
        self.contents.append(
            types.ModelContent(parts=[types.Part.from_text(text=text)])
        )

    def add_model_history(self, content: types.Content):
        self.contents.append(content)

    def add_worker_agent(self, worker_agent: Agent):
        self.agents[worker_agent.agent_config.agent_id] = worker_agent
        # if first agent
        if len(self.agents) == 1:
            self.main_prompt += "\n"
            self.main_prompt += Config().agent_info_prompt

        self.main_prompt += "\n"
        self.main_prompt += f"{worker_agent.agent_config.agent_id} - {worker_agent.agent_config.description}"

    def generate_response(self, text: str) -> AgentOutput:
        print(self.agent_config.agent_id+">")
        if len(self.contents) == 0:
            self.contents.append(
                types.UserContent(parts=[types.Part.from_text(text=self.main_prompt)])
            )

        if text:
            self.add_user_history(text)

        try:
            start = time.time()

            resp = self.client.models.generate_content(
                model=self.agent_config.model_name,
                contents=self.contents,
            )

            end = time.time()

            content = resp.candidates[0].content
            if self.agent_config.save_history:
                self.add_model_history(content=content)

            return AgentOutput(content=content, duration=end - start)
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def process_output(self, output) -> AgentCall:
        agent_call_data = AgentCall()

        for part in output.content.parts:
            if part.text:
                self.term_display.show_text(part.text)
                agent_call_data = identify_agent_call(
                    text=part.text,
                    agent_list=list(self.agents.keys()),
                )

            if part.inline_data:
                self.term_display.show_image(part.inline_data.data)
        return agent_call_data


class GeminiImage(WorkerAgent):
    def __init__(self, agent_config: AgentConfig):
        self.client = genai.Client(api_key=agent_config.api_key)
        self.agent_config = agent_config
        self.term_display = TerminalDisplay()

        self.contents: list[types.Content] = []

    def add_user_history(self, text: str):
        self.contents.append(types.UserContent(parts=[types.Part.from_text(text=text)]))

    def add_model_history(self, content: types.Content):
        self.contents.append(content)

    def generate_response(self, text: str) -> AgentOutput:
        print(self.agent_config.agent_id+">")
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

    def process_output(self, output: AgentOutput) -> types.Content:
        pop_index = None
        for i, part in enumerate(output.content.parts):
            if part.text:
                self.term_display.show_text(part.text)
                pop_index = i

            if part.inline_data:
                self.term_display.show_image(part.inline_data.data)

        if pop_index or pop_index == 0:
            output.content.parts.pop(pop_index)
        return output.content
