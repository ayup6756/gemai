from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    image_dir: str = Field(
        default=Path(__file__).resolve().parent.parent / "data" / "images"
    )

    agent_info_prompt: str = (
        "You are master of worker agent and each agent does something."
        "you can tell the worker agent to do something by saying \"hey {agent name}, query\"."
        "agents already know what they can do so the query should be a task. these agents don't remember their past tasks.\n"
        "Example: \n"
        "lets say you wanna generate an image of dog eating food on mountain and you have an worker agent with name \"ImageMan\" which can create image\n"
        "so you should say\n",
        "hey ImageMan, an image of dog eating food on mountain"
        "it will generate an image and the image will be provided to you"
        "Below is the list of worker agent with their name and their description if there's no entry below this means you have no agent:"
    )