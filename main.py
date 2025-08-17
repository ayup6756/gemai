import os
import dotenv

from agents.gemini import GeminiFlash, GeminiImage
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

    gemini_image_agent = GeminiImage(
        agent_config=AgentConfig(
            api_key=GOOGLE_API_KEY,
            model_name="gemini-2.0-flash-preview-image-generation",
            save_history=True,
            description="This agent can generate image from a given text",
            main_prompt="you are useful image generator you generate high quality images.",
            agent_id="image_gen",
            take_user_input=False
        )
    )

    master.add_worker_agent(gemini_image_agent)
    master.add_tool(GetTimeTool())
    master.add_tool(ScrapePageTool())

    print(master.main_prompt)

    take_user_input = True
    while True:
        if take_user_input:
            user_input = input("user> ")
        else:
            # will take user input in next iteration
            take_user_input = True

        output = master.generate_response(user_input)
        # reset user input for this interaction
        user_input = None

        if not output:
            continue

        print(f"Took {output.duration} seconds")
        agent_call_data = master.process_output(output=output)
        take_user_input |= master.agent_config.take_user_input

        if agent_call_data.name and agent_call_data.query:

            print(agent_call_data.name + ">")

            worker_agent = master.agents[agent_call_data.name]
            output = worker_agent.generate_response(agent_call_data.query)

            if output:
                print(f"Took {output.duration} seconds")
                master.add_user_content_history(
                    worker_agent.process_output(output=output)
                )
                # redirect to user if notify master is false
                take_user_input |= worker_agent.agent_config.take_user_input
            else:
                master.add_user_history("Agent failed")
    

main()
