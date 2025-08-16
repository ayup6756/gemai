import os
import dotenv

from agents.gemini_flash import GeminiFlash
from utils.display import TerminalDisplay
dotenv.load_dotenv()

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


def main():

   term_display = TerminalDisplay()

   gemini_flash_agent = GeminiFlash(
       
   )

   while True:
        pass

main()
