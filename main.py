import os
import dotenv

from agents.gemini import GeminiFlash, GeminiWorker
from agents.tools.get_time_tool import GetTimeTool
from agents.tools.scrape_page_tool import ScrapePageTool
from models.agent_config import AgentConfig

dotenv.load_dotenv()

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


def main():
    master = GeminiFlash(
        agent_config=AgentConfig(
            api_key=GOOGLE_API_KEY,
            model_name="gemini-2.0-flash",
            save_history=True,
            description="Master agent",
            main_prompt="you are useful assistant.",
            agent_id="main",
        )
    )

    gemini_image_agent = GeminiWorker(
        agent_config=AgentConfig(
            api_key=GOOGLE_API_KEY,
            model_name="gemini-2.0-flash-preview-image-generation",
            save_history=False,
            description="This agent can generate image from a given text",
            main_prompt="you are useful image generator you generate high quality images.",
            agent_id="image_gen",
            take_user_input=False
        ),
        response_modalities=["IMAGE", "TEXT"]
    )

    gemini_webscraper_agent = GeminiWorker(
        agent_config=AgentConfig(
            api_key=GOOGLE_API_KEY,
            model_name="gemini-2.0-flash",
            save_history=False,
            description="This agent can scrape website from given url and parse it and do browsing related stuff including search",
            main_prompt="you are webscraping assistant. You can use tools to get textual contents of url with tools and you should process it",
            agent_id="scrape_website",
            take_user_input=False
        ),
        response_modalities=None
    )
    gemini_webscraper_agent.add_tool(ScrapePageTool())

    master.add_worker_agent(gemini_image_agent)
    master.add_worker_agent(gemini_webscraper_agent)
    master.add_tool(GetTimeTool())

    while True:
        user_input = input("user> ")
        if not user_input:
            continue

        master.run(user_input)

main()
