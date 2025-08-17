import json
import undetected_chromedriver as uc
from urllib.parse import urlparse

from models.agent import AgentTool

from bs4 import BeautifulSoup


class ScrapePageTool(AgentTool):
    def __init__(self):
        self.description = "gets the textual contents from webpage after parsing the html you can use it to search on google too with url https://www.google.com/search?q={query}"
        self.tool_id = "ScrapePage"
        self.input_fields_description = {
            "url": "url to get the contents from"
        }
    
    def extract_main_text(self, url) -> str:
        try:
            options = uc.ChromeOptions()
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

            options.binary_location = "/usr/bin/chromium"
            driver = uc.Chrome(options=options)
            driver.get(url)

            status_code = 100
            content_type = "text/plain"
            page_data = driver.page_source

            logs = driver.get_log("performance")

            for log in logs:
                message = log["message"]
                if "Network.responseReceived" not in message:
                    continue
                params = json.loads(message)["message"].get("params")
                if not params:
                    continue
                response = params.get("response")
                if not response:
                    continue
                if url == response["url"]:
                    content_type = response['headers']['content-type']
                    status_code = response['status']


            # for r in driver.requests:
            #     if r.url == url:
            #         status_code = r.response.status_code
            #         content_type = r.response.headers.get_content_type()
            
            driver.quit()

            if "text/html" not in content_type:
                return "content wasn't html"
            
            if status_code != 200:
                return "webpage returned status "+str(status_code)

            soup = BeautifulSoup(page_data, 'html.parser')

            # Remove common unwanted sections
            for tag in soup(['header', 'footer', 'nav', 'aside']):
                tag.decompose()

            # Optionally remove elements by common class/id patterns
            for class_name in ['sidebar', 'side', 'ads', 'advertisement']:
                for tag in soup.select(f'.{class_name}, #{class_name}'):
                    tag.decompose()

            # Try to find candidate content containers
            text = soup.get_text(separator=" ", strip=True)

            # # Extract and clean up the text
            # text = "\n".join(
            #     filter(lambda x: len(x) > 1, [
            #         candidate.get_text(separator='\n', strip=True)
            #         for candidate in candidates
            #     ])
            # )

            print(text)

            return text if text else "failed to scrape"

        except Exception:
            return "failed to scrape"


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