import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")




tavily_client = TavilyClient(
    api_key=api_key
)


def search_web(query: str):
    """Search the web and return relevant search results."""

    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5,
    )

    results = []

    for result in response["results"]:
        results.append(
            {
                "title": result["title"],
                "url": result["url"],
                "content": result.get("content", ""),
            }
        )

    return results

def read_webpage(url: str):
    """Fetch a webpage and return its readable text."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "The webpage took too long to respond.",
            "url": url,
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Could not access webpage: {str(e)}",
            "url": url,
        }

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(
        ["script", "style", "nav", "footer", "header", "aside"]
    ):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    return {
        "success": True,
        "url": url,
        "content": text[:12000],
    }

if __name__ == "__main__":

    results = search_web(
        "latest developments in humanoid robots"
    )

    print("\nSearch Results:\n")

    for i, result in enumerate(results):
        print(f"{i + 1}. {result['title']}")
        print(f"   {result['url']}")
        print()

    if results:

        print("\nReading first result...\n")

        content = read_webpage(
            results[1]["url"]
        )

        if content["success"]:
            print(content["content"][:3000])
        else:
            print("Failed to read webpage:")
            print(content["error"])

TOOLS = [
    search_web,
    read_webpage,
]

TOOL_MAP = {
    "search_web": search_web,
    "read_webpage": read_webpage,
}