import time
from urllib.parse import urlparse
from models.agent import AgentTool
import requests
from bs4 import BeautifulSoup


class ScrapePageTool(AgentTool):
    def __init__(self):
        self.description = "gets the textual contents from webpage after parsing the html"
        self.tool_id = "ScrapePage"
        self.input_fields_description = {
            "url": "url to get the contents from"
        }
    
    def extract_main_text(self, url) -> str:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove common unwanted sections
        for tag in soup(['header', 'footer', 'nav', 'aside']):
            tag.decompose()

        # Optionally remove elements by common class/id patterns
        for class_name in ['sidebar', 'side', 'ads', 'advertisement']:
            for tag in soup.select(f'.{class_name}, #{class_name}'):
                tag.decompose()

        # Try to find the main content
        candidates = soup.find_all(['article', 'div'], recursive=True)

        # Extract and clean up the text
        text = "\n".join(filter(lambda x: len(x) > 1, [candidate.get_text(separator='\n', strip=True) for candidate in candidates]))
        return text

    def validate_url(self, url) -> bool:
        urlparsed = urlparse(url)
        if not (urlparsed.scheme == "https" or urlparsed.scheme == "http") or not urlparsed.netloc:
            return False
        
        return True

    def run(self, query: dict) -> str:
        url =  query.get("url")
        if not url:
            print("url wasn't provided")
            return "url wasn't provided"
        
        if not self.validate_url(url):
            print("url wasn't valid")
            return "url wasn't valid"
        
        print("Scraping the page..", url)
        text = self.extract_main_text(url)
        return f"Below is the textual contents of url {url}\n{text}"