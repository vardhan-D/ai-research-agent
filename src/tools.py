import os

from dotenv import load_dotenv
from tavily import TavilyClient


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


if __name__ == "__main__":

    results = search_web(
        "latest developments in humanoid robots"
    )

    print("\nSearch Results:\n")

    for result in results:
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Content:", result["content"])
        print("-" * 80)