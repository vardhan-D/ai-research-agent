from graph import build_graph


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

        self.state = (
            self.graph.invoke(
                state
            )
        )


        # ------------------------------------------
        # Return final answer
        # ------------------------------------------

        return self.state[
            "final_report"
        ]