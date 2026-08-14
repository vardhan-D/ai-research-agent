import os
import requests

from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup

from state import ResearchState


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

tavily_client = TavilyClient(
    api_key=api_key
)


# --------------------------------------------------
# SEARCH WEB
# --------------------------------------------------

def search_web(query: str):
    """
    Search the web and return relevant search results.
    """

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


# --------------------------------------------------
# READ WEBPAGE
# --------------------------------------------------

def read_webpage(url: str):
    """
    Fetch a webpage and return its readable text.
    """

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

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove unnecessary elements
    for element in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
        ]
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


# --------------------------------------------------
# RESEARCH WEB
# --------------------------------------------------

def research_web(
    query: str,
    state: ResearchState
):
    """
    Search the web, read multiple sources,
    and update the research state.
    """

    print(
        f"\n[Research] Starting research for: {query}"
    )

    # Save query in state
    state.query = query

    # --------------------------------------------------
    # STEP 1: SEARCH
    # --------------------------------------------------

    results = search_web(query)

    # Store search results
    state.search_results = results

    if not results:

        return {
            "query": query,
            "sources": [],
            "message": "No search results found.",
        }

    research = []

    # --------------------------------------------------
    # STEP 2: READ SOURCES
    # --------------------------------------------------

    for result in results:

        url = result["url"]
        title = result["title"]

        print(
            f"\n[Research] Reading: {title}"
        )

        try:

            page = read_webpage(url)

            # ------------------------------------------
            # Failed webpage
            # ------------------------------------------

            if not page.get("success"):

                print(
                    f"[Research] Failed: {url}"
                )

                state.failed_sources.append(
                    {
                        "title": title,
                        "url": url,
                        "reason": page.get(
                            "error",
                            "Unknown error",
                        ),
                    }
                )

                continue

            # ------------------------------------------
            # Extract content
            # ------------------------------------------

            content = page.get(
                "content",
                ""
            )

            if not content.strip():

                state.failed_sources.append(
                    {
                        "title": title,
                        "url": url,
                        "reason": "Empty webpage",
                    }
                )

                continue

            # ------------------------------------------
            # Successful source
            # ------------------------------------------

            source = {
                "title": title,
                "url": url,
                "content": content,
            }

            research.append(source)

            # Save source to state
            state.sources_read.append(source)

            print(
                "[Research] Source collected successfully."
            )

        except Exception as e:

            print(
                f"[Research] Error reading source: {e}"
            )

            state.failed_sources.append(
                {
                    "title": title,
                    "url": url,
                    "reason": str(e),
                }
            )

    # --------------------------------------------------
    # RETURN RESEARCH DATA
    # --------------------------------------------------

    return {
        "query": query,
        "sources": research,
        "source_count": len(research),
        "failed_source_count": len(
            state.failed_sources
        ),
    }

def synthesize_research(state: ResearchState):
    """
    Combine the collected sources into a research context
    that can be analyzed by the LLM.
    """

    if not state.sources_read:
        return {
            "success": False,
            "message": "No sources were successfully read."
        }

    research_context = []

    for source in state.sources_read:

        research_context.append(
            f"""
SOURCE:
{source['title']}

URL:
{source['url']}

CONTENT:
{source['content']}
"""
        )

    context = "\n\n".join(research_context)

    return {
        "success": True,
        "query": state.query,
        "source_count": len(state.sources_read),
        "research_context": context,
    }

# ==================================================
# LLM TOOL SCHEMAS
# ==================================================
#
# IMPORTANT:
#
# These are NOT the Python functions.
#
# These are the descriptions/schema that the LLM
# is allowed to see.
#
# Notice that "state" is NOT included anywhere.
# ==================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for relevant information "
                "and return search results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The search query to use."
                        ),
                    },
                },
                "required": [
                    "query"
                ],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": (
                "Read the contents of a webpage "
                "using its URL."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": (
                            "The URL of the webpage to read."
                        ),
                    },
                },
                "required": [
                    "url"
                ],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "research_web",
            "description": (
                "Perform web research on a topic. "
                "Search multiple sources, read the sources, "
                "and collect the relevant information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The research question or topic."
                        ),
                    },
                },
                "required": [
                    "query"
                ],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "synthesize_research",
            "description": (
                "Combine the collected research sources "
                "into a structured research context for analysis."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },

]


# ==================================================
# PYTHON TOOL MAP
# ==================================================

TOOL_MAP = {

    "search_web": search_web,

    "read_webpage": read_webpage,

    "research_web": research_web,

    "synthesize_research": synthesize_research,

}