from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    image_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent / "data" / "images"
    )
    tmp_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent / "data" / "tmp"
    )

    agent_info_prompt: str = """
You have access to several worker agents, each capable of performing specific tasks that you cannot do yourself.
Agents already understand what they are designed to do, so your query should simply describe the task. They do not retain memory of previous tasks. 
Once agent complete its works don't mention the agent name or that it was called.
whatever task you are given split the task into smaller tasks, don't try to do everything in one go. do step by step.
Don't try to tell the agent to do everything in one go. Split the task into smaller tasks and tell the agent to do one task at a time.
Explain the result after the agents has completed all their tasks

To assign a task to an agent, use the format: "call_worker_agent {agent name}, {task}". Do not use markdown when calling an agent.
The agent will only to call_worker_agent once for each task.

Example:
Suppose you want to generate an image of a dog eating food on a mountain, and you have an agent named "ImageMan" that can create images.
You would say:
call_worker_agent ImageMan, an image of a dog eating food on a mountain.

This will instruct the "ImageMan" agent to generate the image based on your description.

Below is a list of available worker agents, along with their names and descriptions.
If no agents are listed, it means you currently have none.
"""

    tool_info_prompt: str = """
You have access to several tools, each designed to perform a specific task. These tools can do things that you cannot do on your own. You can use them by sending queries in a structured format.

To use a tool, say:
**`call_tool [tool name]`**
and pass the input as a one line **JSON object** on the next line.

The tools already know what they're supposed to do, so your job is to provide them with the correct input values.

Once a tool has returned a result, acknowledge its output and explain it to the user. **Do not call the same tool again unless there's a new query.**

### Example:

Suppose you want to get the Air Quality Index (AQI) of a city, and there's a tool called `GetAQI` that provides this information.

Then you should say:

```
call_tool GetAQI
{"city": "Agra"}
```

The tool will respond with the AQI for Agra. Once it's done, summarize the results for the user.

Below is the list of tools available to you and their queries if there are no queries for certain tool this means it doesn't take any query
If no tools are listed, it means there are none currently available."""