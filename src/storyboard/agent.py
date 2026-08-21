import json
import os

from .llm import StoryboardLLM
from .state import StoryboardState

from .prompts import (
    STORYBOARD_SYSTEM_PROMPT,
    STORYBOARD_PROMPT,
    STORYBOARD_REPAIR_PROMPT,
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
        # SAVE RAW RESPONSE FOR DEBUGGING
        # ------------------------------------------

        os.makedirs(
            "output/debug",
            exist_ok=True
        )


        with open(
            "output/debug/storyboard_raw.txt",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                response
            )


        # ------------------------------------------
        # CLEAN RESPONSE
        # ------------------------------------------

        cleaned_response = self._clean_json_response(
            response
        )


        self.state.final_storyboard = (
            cleaned_response
        )


        # ------------------------------------------
        # FIRST JSON PARSE ATTEMPT
        # ------------------------------------------

        storyboard_data = self._parse_json(
            cleaned_response
        )


        # ------------------------------------------
        # REPAIR JSON IF REQUIRED
        # ------------------------------------------

        if storyboard_data is None:

            print(
                "[Storyboard Agent] "
                "Attempting JSON repair..."
            )


            repair_prompt = (
                STORYBOARD_REPAIR_PROMPT.format(
                    storyboard=cleaned_response
                )
            )


            repaired_response = self.llm.generate(

                system_prompt=(
                    "You repair malformed JSON. "
                    "Return ONLY valid JSON."
                ),

                user_prompt=repair_prompt,

            )


            # ------------------------------------------
            # SAVE REPAIR RESPONSE
            # ------------------------------------------

            with open(
                "output/debug/storyboard_repaired.txt",
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    repaired_response
                )


            repaired_response = (
                self._clean_json_response(
                    repaired_response
                )
            )


            self.state.final_storyboard = (
                repaired_response
            )


            storyboard_data = self._parse_json(
                repaired_response
            )


        # ------------------------------------------
        # STOP IF STILL INVALID
        # ------------------------------------------

        if storyboard_data is None:

            print(
                "[Storyboard Agent] "
                "Storyboard generation failed."
            )

            self.state.scenes = []

            return self.state


        # ------------------------------------------
        # GET SCENES
        # ------------------------------------------

        scenes = storyboard_data.get(
            "scenes",
            []
        )


        # ------------------------------------------
        # VALIDATE / NORMALIZE SCENES
        # ------------------------------------------

        valid_scenes = []


        for index, scene in enumerate(
            scenes,
            start=1
        ):

            if not isinstance(
                scene,
                dict
            ):

                continue


            scene.setdefault(
                "scene_number",
                index
            )

            scene.setdefault(
                "narration",
                ""
            )

            scene.setdefault(
                "visual",
                ""
            )

            scene.setdefault(
                "generation_prompt",
                ""
            )

            scene.setdefault(
                "duration",
                8
            )

            scene.setdefault(
                "transition",
                "cut"
            )


            valid_scenes.append(
                scene
            )


        self.state.scenes = (
            valid_scenes
        )


        print(
            f"[Storyboard Agent] "
            f"Storyboard generated with "
            f"{len(self.state.scenes)} scenes."
        )


        return self.state


    # ==============================================
    # CLEAN LLM RESPONSE
    # ==============================================

    def _clean_json_response(
        self,
        response: str
    ):

        response = response.strip()


        # Remove markdown fences

        if response.startswith(
            "```json"
        ):

            response = response[7:]


        elif response.startswith(
            "```"
        ):

            response = response[3:]


        if response.endswith(
            "```"
        ):

            response = response[:-3]


        response = response.strip()


        # ------------------------------------------
        # KEEP ONLY JSON OBJECT
        # ------------------------------------------

        first_brace = response.find(
            "{"
        )

        last_brace = response.rfind(
            "}"
        )


        if (
            first_brace != -1
            and
            last_brace != -1
        ):

            response = response[
                first_brace:
                last_brace + 1
            ]


        return response


    # ==============================================
    # PARSE JSON
    # ==============================================

    def _parse_json(
        self,
        response: str
    ):

        try:

            return json.loads(
                response
            )


        except json.JSONDecodeError as e:

            print(
                "[Storyboard Agent] "
                "JSON parsing failed."
            )

            print(
                f"[Storyboard Agent] "
                f"Error: {e}"
            )


            # ------------------------------------------
            # PRINT AREA AROUND ERROR
            # ------------------------------------------

            position = e.pos

            start = max(
                0,
                position - 200
            )

            end = min(
                len(response),
                position + 200
            )


            print(
                "\n[Storyboard Agent] "
                "Problem area:"
            )

            print(
                "------------------------------"
            )

            print(
                response[start:end]
            )

            print(
                "------------------------------"
            )


            return None