import json
import re
from models.agent import AgentCall, AgentTool, ToolCall

class AgentUtils:

    @staticmethod
    def identify_agent_call(text: str, agent_list: list[str]) -> AgentCall:

        call_agent_line = None
        for line in text.split("\n"):
            if line.startswith("call_worker_agent"):
                call_agent_line = line
        
        if not call_agent_line:
            return AgentCall()
        
        agent_call_regex = re.compile(r"call_worker_agent\s+(\w+),\s+(.*)")
        match = agent_call_regex.match(call_agent_line)

        if not match:
            return AgentCall()
        
        if match.lastindex != 2:
            return AgentCall()
        
        name = match.group(1)
        query = match.group(2)

        if not name.strip() or not query.strip():
            return AgentCall()
        
        if name not in agent_list:
            return AgentCall()

        return AgentCall(name=name, query=query)
       
    @staticmethod
    def identify_tool_call(text: str, tool_list: list[str]) -> ToolCall:

        out = ToolCall()
        call_tool_line = None
        query = None
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            if line.startswith("call_tool"):
                call_tool_line = line
                if (idx + 1) < len(lines):
                    query = lines[idx + 1]
                break

        
        if not call_tool_line:
            return out
        
        tool_call_regex = re.compile(r"call_tool\s+(\w+)\s?\n?(\{.+\})?\n?")
        match = tool_call_regex.match(call_tool_line)

        if not match:
            return out
        
        if match.lastindex < 1:
            return out
        
        name = match.group(1)

        if not name.strip():
            return out
        
        if name not in tool_list:
            return out
        
        query = {}
        if match.lastindex > 1:
            querystr = match.group(2)
            try:
                query = json.loads(querystr)
            except json.JSONDecodeError:
                pass
        
        return ToolCall(name=name, query=query)
 