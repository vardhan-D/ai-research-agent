from .graph import build_graph
from .state import ResearchState


class Agent:

    def __init__(self):

        self.graph = build_graph()

        self.state = None


    def run(
        self,
        prompt
    ):

        # ------------------------------------------
        # Initial LangGraph state
        # ------------------------------------------

        state = {

            "query": prompt,

            "search_results": [],

            "sources_read": [],

            "failed_sources": [],

            "findings": [],

            "gaps": [],

            "final_report": "",

            "research_attempts": 0,

            "sources_relevant": False,
        }


        # ------------------------------------------
        # Run graph
        # ------------------------------------------

        final_state = self.graph.invoke(
            state
        )


        # ------------------------------------------
        # Convert LangGraph dict
        # back to ResearchState
        # ------------------------------------------

        self.state = ResearchState(

            query=final_state.get(
                "query",
                ""
            ),

            search_results=final_state.get(
                "search_results",
                []
            ),

            sources_read=final_state.get(
                "sources_read",
                []
            ),

            failed_sources=final_state.get(
                "failed_sources",
                []
            ),

            findings=final_state.get(
                "findings",
                []
            ),

            gaps=final_state.get(
                "gaps",
                []
            ),

            final_report=final_state.get(
                "final_report",
                ""
            ),
        )


        # ------------------------------------------
        # Return final answer
        # ------------------------------------------

        return self.state.final_report