from typing import TypedDict
import json

from langgraph.graph import StateGraph, START, END

from state import ResearchState

from tools import (
    research_web,
    validate_sources,
    synthesize_research,
    generate_report,
)

from llm import LLM


# ==================================================
# LANGGRAPH STATE
# ==================================================

class GraphState(TypedDict):

    query: str

    search_results: list

    sources_read: list

    failed_sources: list

    findings: list

    gaps: list

    final_report: str

    research_attempts: int

    sources_relevant: bool


# ==================================================
# LLM
# ==================================================

llm = LLM()


# ==================================================
# GRAPH STATE → RESEARCH STATE
# ==================================================

def make_research_state(state: GraphState):

    return ResearchState(

        query=state["query"],

        search_results=state["search_results"],

        sources_read=state["sources_read"],

        failed_sources=state["failed_sources"],

        findings=state["findings"],

        gaps=state["gaps"],

        final_report=state["final_report"],
    )


# ==================================================
# NODE 1 — RESEARCH
# ==================================================

def research_node(state: GraphState):

    print("\n==============================")
    print("[Graph] RESEARCH")
    print("==============================")

    attempts = (
        state["research_attempts"] + 1
    )

    print(
        f"[Graph] Research attempt: {attempts}"
    )

    research_state = make_research_state(
        state
    )

    # ----------------------------------------------
    # Fresh research on every attempt
    # ----------------------------------------------

    research_state.search_results = []

    research_state.sources_read = []

    research_state.failed_sources = []

    # ----------------------------------------------
    # Adaptive query
    # ----------------------------------------------

    if attempts == 1:

        research_query = state["query"]

    else:

        research_query = (
            f"{state['query']} "
            "latest 2026 breakthroughs research "
            "companies humanoid robots industrial "
            "robots embodied AI robotics"
        )

    print(
        f"[Graph] Search query: "
        f"{research_query}"
    )

    # ----------------------------------------------
    # Run research
    # ----------------------------------------------

    research_web(
        query=research_query,
        state=research_state,
    )

    return {

        "query": state["query"],

        "search_results":
            research_state.search_results,

        "sources_read":
            research_state.sources_read,

        "failed_sources":
            research_state.failed_sources,

        "findings":
            research_state.findings,

        "gaps":
            research_state.gaps,

        "final_report":
            research_state.final_report,

        "research_attempts":
            attempts,

        "sources_relevant":
            False,
    }


# ==================================================
# NODE 2 — VALIDATE SOURCES
# ==================================================

def validate_node(state: GraphState):

    print("\n==============================")
    print("[Graph] VALIDATE SOURCES")
    print("==============================")

    research_state = make_research_state(
        state
    )

    result = validate_sources(
        state=research_state
    )

    valid_sources = result.get(
        "valid_sources",
        []
    )

    # ----------------------------------------------
    # Deduplicate URLs
    # ----------------------------------------------

    unique_sources = []

    seen_urls = set()

    for source in valid_sources:

        url = source.get(
            "url",
            ""
        )

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_sources.append(
            source
        )

    research_state.sources_read = (
        unique_sources
    )

    print(
        f"[Graph] Valid sources: "
        f"{len(unique_sources)}"
    )

    print(
        f"[Graph] Rejected sources: "
        f"{result.get('rejected_count', 0)}"
    )

    return {

        "query":
            research_state.query,

        "search_results":
            research_state.search_results,

        "sources_read":
            research_state.sources_read,

        "failed_sources":
            research_state.failed_sources,

        "findings":
            research_state.findings,

        "gaps":
            research_state.gaps,

        "final_report":
            research_state.final_report,

        "research_attempts":
            state["research_attempts"],

        "sources_relevant":
            False,
    }


# ==================================================
# NODE 3 — PER-SOURCE RELEVANCE
# ==================================================

def relevance_node(state: GraphState):

    print("\n==============================")
    print("[Graph] CHECK SOURCE RELEVANCE")
    print("==============================")

    sources = state["sources_read"]

    if not sources:

        print(
            "[Graph] No sources available."
        )

        return {
            "sources_relevant": False,
            "sources_read": [],
        }

    # ----------------------------------------------
    # Build source list
    # ----------------------------------------------

    source_summary = ""

    for i, source in enumerate(
        sources,
        1
    ):

        source_summary += f"""

SOURCE {i}

Title:
{source["title"]}

URL:
{source["url"]}

Content:
{source["content"][:2500]}

--------------------------------
"""

    # ----------------------------------------------
    # Ask LLM to evaluate EACH source
    # ----------------------------------------------

    prompt = f"""
You are a strict research source evaluator.

Research question:

{state["query"]}

Evaluate EVERY source individually.

A source is relevant only if its content directly
helps answer the research question.

Do not judge a source based only on keywords.

For example, if the question is about robotics,
a general AI article should be considered irrelevant
unless it specifically discusses robotics or robotic
systems.

Sources:

{source_summary}

Return ONLY valid JSON.

The JSON MUST be an array.

There must be exactly one object for every source.

Use this exact format:

[
    {{
        "source_number": 1,
        "relevant": true,
        "reason": "short explanation"
    }},
    {{
        "source_number": 2,
        "relevant": false,
        "reason": "short explanation"
    }}
]

Do not return markdown.
Do not return additional text.
"""

    response = llm.chat(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    answer = (
        response.message.content
        .strip()
    )

    print(
        "[Graph] Relevance response:"
    )

    print(answer)

    # ==================================================
    # PARSE RESPONSE
    # ==================================================

    decisions = []

    try:

        cleaned = answer

        # Remove accidental markdown fences

        if "```json" in cleaned:

            cleaned = (
                cleaned
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

        elif "```" in cleaned:

            cleaned = (
                cleaned
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

        decisions = json.loads(
            cleaned
        )

        # Make sure response is a list

        if not isinstance(
            decisions,
            list
        ):

            raise ValueError(
                "Expected a JSON list."
            )

    except Exception as e:

        print(
            "[Graph] Failed to parse "
            f"relevance response: {e}"
        )

        # Conservative fallback:
        # don't throw away sources if the
        # evaluator itself fails.

        return {
            "sources_relevant": True,
            "sources_read": sources,
        }

    # ==================================================
    # FILTER SOURCES
    # ==================================================

    relevant_sources = []

    irrelevant_sources = []

    for decision in decisions:

        try:

            source_number = int(
                decision[
                    "source_number"
                ]
            )

            is_relevant = bool(
                decision[
                    "relevant"
                ]
            )

            reason = decision.get(
                "reason",
                ""
            )

        except Exception:

            continue

        # ------------------------------------------
        # Make sure source number is valid
        # ------------------------------------------

        if (
            source_number < 1
            or
            source_number > len(sources)
        ):

            continue

        source = sources[
            source_number - 1
        ]

        if is_relevant:

            relevant_sources.append(
                source
            )

            print(
                f"[Graph] ✓ Relevant: "
                f"{source['title']}"
            )

        else:

            irrelevant_sources.append(
                source
            )

            print(
                f"[Graph] ✗ Irrelevant: "
                f"{source['title']}"
            )

            print(
                f"        Reason: {reason}"
            )

    # ==================================================
    # FALLBACK IF LLM MISSED SOURCES
    # ==================================================

    # If the LLM failed to provide a decision
    # for some sources, keep those sources rather
    # than accidentally deleting valid research.

    evaluated_numbers = set()

    for decision in decisions:

        try:

            evaluated_numbers.add(
                int(
                    decision[
                        "source_number"
                    ]
                )
            )

        except Exception:

            pass

    for i, source in enumerate(
        sources,
        1
    ):

        if i not in evaluated_numbers:

            print(
                f"[Graph] ? No decision for: "
                f"{source['title']}"
            )

            relevant_sources.append(
                source
            )

    # ==================================================
    # RESULT
    # ==================================================

    print(
        f"\n[Graph] Relevant sources: "
        f"{len(relevant_sources)}"
    )

    print(
        f"[Graph] Irrelevant sources removed: "
        f"{len(irrelevant_sources)}"
    )

    # Need at least 2 useful sources
    # for a reasonably reliable report.

    enough_sources = (
        len(relevant_sources) >= 2
    )

    return {

        "sources_read":
            relevant_sources,

        "sources_relevant":
            enough_sources,
    }


# ==================================================
# CONDITIONAL ROUTING
# ==================================================

def route_after_relevance(
    state: GraphState
):

    # ----------------------------------------------
    # Enough relevant sources
    # ----------------------------------------------

    if state[
        "sources_relevant"
    ]:

        print(
            "[Graph] Enough relevant "
            "sources found."
        )

        return "synthesize"

    # ----------------------------------------------
    # Maximum attempts
    # ----------------------------------------------

    if (
        state["research_attempts"]
        >= 2
    ):

        print(
            "[Graph] Maximum research "
            "attempts reached."
        )

        print(
            "[Graph] Continuing with "
            "available sources."
        )

        return "synthesize"

    # ----------------------------------------------
    # Need more research
    # ----------------------------------------------

    print(
        "[Graph] Not enough relevant "
        "sources."
    )

    print(
        "[Graph] Starting another "
        "research attempt..."
    )

    return "research"


# ==================================================
# NODE 4 — SYNTHESIZE
# ==================================================

def synthesize_node(
    state: GraphState
):

    print("\n==============================")
    print("[Graph] SYNTHESIZE")
    print("==============================")

    research_state = make_research_state(
        state
    )

    result = synthesize_research(
        state=research_state
    )

    if not result.get(
        "success"
    ):

        print(
            "[Graph] Synthesis failed."
        )

        return {
            "findings": []
        }

    prompt = result[
        "instruction"
    ]

    response = llm.chat(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    findings_text = (
        response.message.content
    )

    research_state.findings = [
        findings_text
    ]

    print(
        "[Graph] Findings generated."
    )

    return {

        "query":
            research_state.query,

        "search_results":
            research_state.search_results,

        "sources_read":
            research_state.sources_read,

        "failed_sources":
            research_state.failed_sources,

        "findings":
            research_state.findings,

        "gaps":
            research_state.gaps,

        "final_report":
            research_state.final_report,

        "research_attempts":
            state["research_attempts"],

        "sources_relevant":
            state["sources_relevant"],
    }


# ==================================================
# NODE 5 — GENERATE REPORT
# ==================================================

def report_node(
    state: GraphState
):

    print("\n==============================")
    print("[Graph] GENERATE REPORT")
    print("==============================")

    research_state = make_research_state(
        state
    )

    result = generate_report(
        state=research_state
    )

    if not result.get(
        "success"
    ):

        print(
            "[Graph] Report generation failed."
        )

        return {
            "final_report": ""
        }

    research_state.final_report = (
        result["report"]
    )

    return {

        "query":
            research_state.query,

        "search_results":
            research_state.search_results,

        "sources_read":
            research_state.sources_read,

        "failed_sources":
            research_state.failed_sources,

        "findings":
            research_state.findings,

        "gaps":
            research_state.gaps,

        "final_report":
            research_state.final_report,

        "research_attempts":
            state["research_attempts"],

        "sources_relevant":
            state["sources_relevant"],
    }


# ==================================================
# BUILD GRAPH
# ==================================================

def build_graph():

    builder = StateGraph(
        GraphState
    )

    # ----------------------------------------------
    # Nodes
    # ----------------------------------------------

    builder.add_node(
        "research",
        research_node
    )

    builder.add_node(
        "validate",
        validate_node
    )

    builder.add_node(
        "relevance",
        relevance_node
    )

    builder.add_node(
        "synthesize",
        synthesize_node
    )

    builder.add_node(
        "report",
        report_node
    )

    # ----------------------------------------------
    # START → RESEARCH
    # ----------------------------------------------

    builder.add_edge(
        START,
        "research"
    )

    # ----------------------------------------------
    # RESEARCH → VALIDATE
    # ----------------------------------------------

    builder.add_edge(
        "research",
        "validate"
    )

    # ----------------------------------------------
    # VALIDATE → RELEVANCE
    # ----------------------------------------------

    builder.add_edge(
        "validate",
        "relevance"
    )

    # ----------------------------------------------
    # RELEVANCE → CONDITIONAL
    # ----------------------------------------------

    builder.add_conditional_edges(

        "relevance",

        route_after_relevance,

        {
            "research":
                "research",

            "synthesize":
                "synthesize",
        }
    )

    # ----------------------------------------------
    # SYNTHESIZE → REPORT
    # ----------------------------------------------

    builder.add_edge(
        "synthesize",
        "report"
    )

    # ----------------------------------------------
    # REPORT → END
    # ----------------------------------------------

    builder.add_edge(
        "report",
        END
    )

    # ----------------------------------------------
    # COMPILE
    # ----------------------------------------------

    return builder.compile()