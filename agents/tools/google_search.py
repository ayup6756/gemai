import json
import undetected_chromedriver as webdriver
# import selenium.webdriver as webdriver
from urllib.parse import urlparse
from models.agent import AgentTool

from bs4 import BeautifulSoup


class GoogleSearchTool(AgentTool):
    def __init__(self):
        self.description = "performs a Google search and returns the top results."
        self.tool_id = "GoogleSearchTool"
        self.input_fields_description = {
            "query": "query to search on Google"
        }
    
    def extract_data(self, url) -> str:
        try:
            # webdriver.DesiredCapabilities.CHROME[''] = {'performance': 'ALL'}
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-gpu")
            # options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--incognito")
            # options.add_argument("--disable-extensions")
            # options.add_argument("--disable-infobars")
            # options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

            options.binary_location = "/usr/bin/chromium"
            driver = webdriver.Chrome(options=options)
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

        except Exception as e:
            print(f"Error while scraping the page: {e}")
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
        text = self.extract_data(url)
        return f"Below is the textual contents of url {url}\n{text}"