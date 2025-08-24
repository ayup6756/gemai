import json
from pathlib import Path
from pydantic import BaseModel
import undetected_chromedriver as webdriver

# import selenium.webdriver as webdriver
from models.agent import AgentTool

from bs4 import BeautifulSoup
from bs4.element import Tag


class GoogleSearchResult(BaseModel):
    url: str


class GoogleSearchTool(AgentTool):
    def __init__(self):
        self.description = "performs a Google search and returns the top results."
        self.tool_id = "GoogleSearchTool"
        self.input_fields_description = {"query": "query to search on Google"}

    def extract_data(self, url) -> str | None:
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
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

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
                    content_type = response["headers"]["content-type"]
                    status_code = response["status"]

            # for r in driver.requests:
            #     if r.url == url:
            #         status_code = r.response.status_code
            #         content_type = r.response.headers.get_content_type()

            driver.quit()

            if "text/html" not in content_type:
                return "content wasn't html"

            if status_code != 200:
                return "webpage returned status " + str(status_code)

            return page_data

        except Exception as e:
            print(f"Error while scraping the page: {e}")
            return None

    def find_first_element(
        self, tag: str, elem: Tag, depth: int
    ) -> Tag:
        out: Tag = None

        for i in range(depth):
            if i == 0:
                out = elem
                result = elem.find(tag, recursive=False)
                if not result:
                    break
                out = result
            else:
                result = out.find(tag, recursive=False)
                if not result:
                    break
                out = result

        return out

    def parse_google_search_results(self, query: str) -> list[GoogleSearchResult]:
        data = self.extract_data(f"https://www.google.com/search?q={query}")
        (Path(__file__).parent / ".." / ".." / "data" / "google.html").write_text(data)
        if not data:
            return []
        soup = BeautifulSoup(data, "html.parser")
        results = []

        search_div = soup.find("div", {"id": "search"})

        if not search_div:
            print("No search results found.")
            return []
        (Path(__file__).parent / ".." / ".." / "data" / "search.html").write_text(
            str(search_div)
        )

        results_div: Tag = self.find_first_element("div", search_div, 2)

        results_ = results_div.find_all("div", recursive=False)

        for result in results_:
            if not result:
                continue
            if len(result.contents) == 1:
                result = self.find_first_element("div", result, 5)
                atag = result.find("a", attrs={
                    "href":True,
                    "ping": True,
                    "data-ved": True,
                })

                if atag:
                    results.append(GoogleSearchResult(url=atag["href"]))

        return results

    def run(self, query: dict) -> str:
        q = query.get("query")
        if not q:
            print("query wasn't provided")
            return "query wasn't provided"

        print("Seaching the query..", q)
        results = self.parse_google_search_results(q)

        if len(results) == 0:
            return "No results found for the query: " + q

        output = "Results of query: " + q + "\n"
        for i, result in enumerate(results):
            output += f"{i + 1}. {result.url}\n"

        return output
