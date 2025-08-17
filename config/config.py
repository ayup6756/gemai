from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    image_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent / "data" / "images"
    )
    tmp_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent / "data" / "tmp"
    )

    agent_info_prompt: str = (
        "You are master of worker agent and each agent does something. you can use these agents do to things you can't do yourself. These agent will respond as user.\n"
        'You can tell the worker agent to do something by saying "call_worker_agent {agent name}, query". Don\'t use markdown while calling an agent\n'
        "Agents already know what they can do, so the query should be a task. "
        "These agents don't remember their past tasks and you should acknowledge their work and tell user about it\n\n"
        "Example:\n"
        'Let\'s say you want to generate an image of a dog eating food on a mountain, and you have a worker agent named "ImageMan" that can create images.\n'
        "Then you should say:\n"
        "call_worker_agent ImageMan, an image of dog eating food on mountain.\n\n"
        "It will generate an image, don't call it again after its done\n\n"
        "Below is the list of worker agents with their name and description. "
        "If there's no entry below, it means you have no agents:"
    )
