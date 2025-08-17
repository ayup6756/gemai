import time
from models.agent import AgentTool


class GetTimeTool(AgentTool):
    def __init__(self):
        self.description = "gets the current time"
        self.tool_id = "GetTime"
        self.input_fields_description = {}
    
    def run(self, query: dict) -> str:
        print("Getting time....")
        return f"Time: {time.strftime("%c %Z")}"