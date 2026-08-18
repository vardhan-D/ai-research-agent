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


        storyboard = self.llm.generate(

            system_prompt=
                STORYBOARD_SYSTEM_PROMPT,

            user_prompt=
                prompt,

        )


        # ------------------------------------------
        # SAVE OUTPUT
        # ------------------------------------------

        self.state.final_storyboard = storyboard


        print(
            "[Storyboard Agent] "
            "Storyboard generated."
        )


        return self.state