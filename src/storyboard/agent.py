import json

from .llm import StoryboardLLM
from .state import StoryboardState

from .prompts import (
    STORYBOARD_SYSTEM_PROMPT,
    STORYBOARD_PROMPT,
)


class StoryboardAgent:

    def __init__(self):

        self.llm = StoryboardLLM()

        self.state = None


    def run(
        self,
        script: str
    ):

        # ------------------------------------------
        # CREATE STATE
        # ------------------------------------------

        self.state = StoryboardState(

            script=script

        )


        # ------------------------------------------
        # BUILD PROMPT
        # ------------------------------------------

        prompt = STORYBOARD_PROMPT.format(

            script=script

        )


        # ------------------------------------------
        # GENERATE STORYBOARD
        # ------------------------------------------

        print(
            "\n[Storyboard Agent] "
            "Generating storyboard..."
        )


        response = self.llm.generate(

            system_prompt=
                STORYBOARD_SYSTEM_PROMPT,

            user_prompt=
                prompt,

        )


        # ------------------------------------------
        # SAVE RAW RESPONSE
        # ------------------------------------------

        self.state.final_storyboard = response


        # ------------------------------------------
        # PARSE JSON
        # ------------------------------------------

        try:

            storyboard_data = json.loads(
                response
            )

            self.state.scenes = (
                storyboard_data.get(
                    "scenes",
                    []
                )
            )


            print(
                f"[Storyboard Agent] "
                f"Storyboard generated with "
                f"{len(self.state.scenes)} scenes."
            )


        except json.JSONDecodeError as e:

            print(
                "[Storyboard Agent] "
                "Failed to parse storyboard JSON."
            )

            print(
                f"[Storyboard Agent] Error: {e}"
            )

            self.state.scenes = []


        return self.state