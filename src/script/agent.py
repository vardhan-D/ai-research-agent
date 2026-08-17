from .llm import ScriptLLM
from .state import ScriptState
from .prompts import (
    SCRIPT_SYSTEM_PROMPT,
    SCRIPT_PROMPT,
)
from .tools import format_sources


class ScriptAgent:

    def __init__(self):

        self.llm = ScriptLLM()

        self.state = None


    def run(
        self,
        topic: str,
        research: str,
        sources: list
    ):

        # ------------------------------------------
        # Create state
        # ------------------------------------------

        self.state = ScriptState(

            topic=topic,

            research=research,

            sources=sources,
        )


        # ------------------------------------------
        # Format sources
        # ------------------------------------------

        sources_text = format_sources(
            sources
        )


        # ------------------------------------------
        # Build prompt
        # ------------------------------------------

        prompt = SCRIPT_PROMPT.format(

            topic=topic,

            research=research,

            sources=sources_text,
        )


        # ------------------------------------------
        # Generate script
        # ------------------------------------------

        print(
            "\n[Script Agent] Generating script..."
        )


        draft = self.llm.generate(

            system_prompt=
                SCRIPT_SYSTEM_PROMPT,

            user_prompt=
                prompt,
        )


        # ------------------------------------------
        # Save draft
        # ------------------------------------------

        self.state.draft = draft

        self.state.final_script = draft

        self.state.script_valid = bool(
            draft.strip()
        )


        print(
            "[Script Agent] Script generated."
        )


        return self.state


    # ==========================================
    # RUN FROM RESEARCH AGENT
    # ==========================================

    def run_from_research(
        self,
        research_state
    ):

        topic = research_state.query

        findings = research_state.findings

        


        research_text = "\n\n".join(
            str(finding)
            for finding in findings
        )


        return self.run(

            topic=topic,

            research=research_text,

            sources=[],
        )