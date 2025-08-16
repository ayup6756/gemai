import re
from models.agent import AgentCall


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
    