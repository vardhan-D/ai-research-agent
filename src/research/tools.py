import os
import requests

from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup

from .state import ResearchState

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
        "message": (
        "Research completed successfully. "
        "Use the collected sources to synthesize "
        "the final answer."
        ),
    }

def synthesize_research(state: ResearchState):
    """
    Analyze the sources collected in ResearchState
    and extract the important findings.
    """

    if not state.sources_read:
        return {
            "success": False,
            "message": "No sources available for synthesis."
        }

    research_context = ""

    for i, source in enumerate(state.sources_read, 1):
        research_context += f"""
SOURCE {i}
Title: {source['title']}
URL: {source['url']}

Content:
{source['content'][:6000]}

----------------------------------------
"""

    prompt = f"""
You are a research analyst.

Research question:
{state.query}

Below are sources collected from the web.

{research_context}

Analyze these sources and extract the important findings.

Rules:
- Only use information supported by the sources.
- Do not invent facts.
- Remove irrelevant information.
- Combine overlapping findings.
- Identify important developments, trends, facts, or conclusions.
- Mention the source number supporting each finding.

Return the findings as a numbered list.
"""

    return {
        "success": True,
        "query": state.query,
        "research_context": research_context,
        "instruction": prompt,
    }

def validate_sources(state: ResearchState):
    """
    Validate the sources collected during research.
    """

    valid_sources = []
    rejected_sources = []

    for source in state.sources_read:

        title = source.get("title", "")
        url = source.get("url", "")
        content = source.get("content", "")

        # Basic validation
        if not title.strip():
            rejected_sources.append({
                "url": url,
                "reason": "Missing title"
            })
            continue

        if not url.startswith("http"):
            rejected_sources.append({
                "title": title,
                "reason": "Invalid URL"
            })
            continue

        if len(content.strip()) < 200:
            rejected_sources.append({
                "title": title,
                "url": url,
                "reason": "Insufficient content"
            })
            continue

        valid_sources.append(source)

    return {
        "success": True,
        "valid_sources": valid_sources,
        "rejected_sources": rejected_sources,
        "valid_count": len(valid_sources),
        "rejected_count": len(rejected_sources),
    }

def generate_report(state: ResearchState):
    """
    Generate a structured final research report
    from the validated research findings.
    """

    if not state.findings:
        return {
            "success": False,
            "message": "No research findings available."
        }

    findings_text = "\n\n".join(
        str(finding)
        for finding in state.findings
    )

    sources_text = "\n".join(
        f"- {source['title']} — {source['url']}"
        for source in state.sources_read
    )

    report = f"""
# Research Report

## Research Question

{state.query}

## Key Findings

{findings_text}

## Sources

{sources_text}
""".strip()

    state.final_report = report

    return {
        "success": True,
        "report": report,
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
    {
        "type": "function",
        "function": {
            "name": "validate_sources",
            "description": (
                "Validate the sources collected during research. "
                "Check whether the sources contain valid URLs, "
                "meaningful content, and sufficient information."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": (
                "Generate a structured research report "
                "using the findings and sources collected "
                "during the research process."
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

    "validate_sources": validate_sources,

    "generate_report": generate_report,
}