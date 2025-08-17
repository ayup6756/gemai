import time
from google import genai
from google.genai import types
from config.config import Config
from models.agent_config import AgentConfig
from models.agent import (
    Agent,
    AgentCall,
    AgentOutput,
    AgentTool,
    MasterAgent,
    ToolCall,
    WorkerAgent,
)
from utils.agent import AgentUtils
from utils.display import TerminalDisplay
from typing import Dict


class GeminiFlash(MasterAgent):
    def __init__(self, agent_config: AgentConfig):
        self.client = genai.Client(api_key=agent_config.api_key)
        self.agent_config = agent_config
        self.agents: Dict[str, Agent] = {}
        self.tools: Dict[str, AgentTool] = {}
        self.main_prompt = agent_config.main_prompt
        self.term_display = TerminalDisplay()

        self.contents: list[types.Content] = []

    def add_user_history(self, text: str):
        self.contents.append(types.UserContent(parts=[types.Part.from_text(text=text)]))

    def add_user_content_history(self, content: types.Content):
        self.contents.append(types.UserContent(parts=content.parts))

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
        self.main_prompt += str(worker_agent)

    def generate_response(self, text: str) -> AgentOutput:
        self.agent_config.recall_itself = False
        print(self.agent_config.agent_id + ">")
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
        self.agent_config.recall_itself = False
        agent_call_data = AgentCall()
        tool_call_data = ToolCall()

        for part in output.content.parts:
            if part.text:
                self.term_display.show_text(part.text)
                agent_call_data = AgentUtils.identify_agent_call(
                    text=part.text,
                    agent_list=list(self.agents.keys()),
                )
                tool_call_data = AgentUtils.identify_tool_call(
                    text=part.text,
                    tool_list=list(self.tools.keys()),
                )

                if agent_call_data.name and agent_call_data.query:
                    self.agent_config.recall_itself = True

                if tool_call_data.name:
                    print(f"Tool {tool_call_data.name}>")
                    tool = self.tools[tool_call_data.name]
                    tool_output = tool.run(tool_call_data.query)
                    if tool_output:
                        self.add_model_text_history(tool_output)
                    else:
                        self.add_model_text_history("Tool failed")
                    self.agent_config.recall_itself = True

            if part.inline_data:
                self.term_display.show_image(part.inline_data.data)

        return agent_call_data

    def add_tool(self, tool: AgentTool):
        self.tools[tool.tool_id] = tool
        # if first agent
        if len(self.tools) == 1:
            self.main_prompt += "\n"
            self.main_prompt += Config().tool_info_prompt

        self.main_prompt += "\n"
        self.main_prompt += str(tool)
    
    def run(self, text: str):
        output = self.generate_response(text=text)

        if not output:
            content = types.UserContent(parts=[types.Part.from_text(text="Agent failed")])
            self.add_model_history(content=content)
            return content
        
        print(f"Took {output.duration} seconds")

        agent_call_data = self.process_output(output=output)

        content = None

        if agent_call_data.name and agent_call_data.query:
            agent = self.agents[agent_call_data.name]
            content = agent.run(agent_call_data.query)
            self.add_model_history(content=content)

        while self.agent_config.recall_itself:
            # reset the recall_itself
            self.agent_config.recall_itself = False
            output = self.generate_response(text=None)
            if not output:
                content = types.UserContent(parts=[types.Part.from_text(text="Agent failed")])
                self.add_model_history(content=content)
                return content
            agent_call_data = self.process_output(output=output)

            if agent_call_data.name and agent_call_data.query:
                agent = self.agents[agent_call_data.name]
                content = agent.run(agent_call_data.query)
                self.add_model_history(content=content)

        return content


class GeminiWorker(WorkerAgent):
    def __init__(self, agent_config: AgentConfig, response_modalities: list[str]):
        self.client = genai.Client(api_key=agent_config.api_key)
        self.agent_config = agent_config
        self.main_prompt = agent_config.main_prompt
        self.term_display = TerminalDisplay()
        self.tools: Dict[str, AgentTool] = {}
        self.response_modalities = response_modalities

        self.contents: list[types.Content] = []

    def add_user_history(self, text: str):
        self.contents.append(types.UserContent(parts=[types.Part.from_text(text=text)]))

    def add_model_history(self, content: types.Content):
        self.contents.append(content)

    def generate_response(self, text: str) -> AgentOutput:
        print(self.agent_config.agent_id + ">")
        if len(self.contents) == 0:
            self.contents.append(
                types.UserContent(parts=[types.Part.from_text(text=self.main_prompt)])
            )
        if text:
            if self.agent_config.save_history:
                self.add_user_history(text)
            else:
                self.contents = [
                    types.UserContent(parts=[types.Part.from_text(text=self.main_prompt)]),
                    types.UserContent(parts=[types.Part.from_text(text=text)]),
                ]

        try:
            start = time.time()

            resp = self.client.models.generate_content(
                model=self.agent_config.model_name,
                contents=self.contents,
                config= types.GenerateContentConfig(
                    response_modalities=self.response_modalities
                ) if self.response_modalities else None,
            )

            end = time.time()

            content = resp.candidates[0].content
            if self.agent_config.save_history:
                self.add_model_history(content=content)

            return AgentOutput(content=content, duration=end - start)
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def add_tool(self, tool: AgentTool):
        self.tools[tool.tool_id] = tool
        # if first agent
        if len(self.tools) == 1:
            self.main_prompt += "\n"
            self.main_prompt += Config().tool_info_prompt

        self.main_prompt += "\n"
        self.main_prompt += str(tool)

    def process_output(self, output: AgentOutput) -> types.Content:
        parts = []

        for i, part in enumerate(output.content.parts):
            if part.text:
                self.term_display.show_text(part.text)
                tool_call_data = AgentUtils.identify_tool_call(
                    text=part.text,
                    tool_list=list(self.tools.keys()),
                )
                parts.append(part)

                if tool_call_data.name:
                    print(f"Tool {tool_call_data.name}>")
                    tool = self.tools[tool_call_data.name]
                    tool_output = tool.run(tool_call_data.query)
                    if tool_output:
                        self.add_model_history(types.ModelContent(parts=[types.Part.from_text(text=tool_output)]))
                    else:
                        self.add_model_history(types.ModelContent(parts=[types.Part.from_text(text="Tool failed")]))

                    self.agent_config.recall_itself = True


            if part.inline_data:
                self.term_display.show_image(part.inline_data.data)

        output.content.parts = parts
        return output.content
    
    def run(self, text: str) -> types.Content:
        self.agent_config.save_history = True

        output = self.generate_response(text=text)

        if not output:
            return types.ModelContent(parts=[types.Part.from_text(text="Agent failed")])
        
        print(f"Took {output.duration} seconds")

        content = self.process_output(output=output)

        while self.agent_config.recall_itself:
            # reset the recall_itself
            self.agent_config.recall_itself = False
            output = self.generate_response(text=None)
            if not output:
                return types.ModelContent(parts=[types.Part.from_text(text="Agent failed")])
            content = self.process_output(output=output)

        
        self.agent_config.save_history = False

        return content
