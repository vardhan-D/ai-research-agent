from .state import VoiceState
from .tools import generate_scene_audio


class VoiceAgent:

    def __init__(self):

        self.state = None


    def run(
        self,
        scenes: list
    ):

        # ------------------------------------------
        # CREATE STATE
        # ------------------------------------------

        self.state = VoiceState(
            scenes=scenes
        )


        print(
            "\n[Voice Agent] "
            "Generating narration audio..."
        )


        # ------------------------------------------
        # GENERATE AUDIO FOR EACH SCENE
        # ------------------------------------------

        for scene in scenes:

            scene_number = scene.get(
                "scene_number"
            )

            narration = scene.get(
                "narration",
                ""
            )


            if not narration:

                print(
                    f"[Voice Agent] "
                    f"Scene {scene_number} "
                    f"has no narration. Skipping."
                )

                continue


            print(
                f"[Voice Agent] "
                f"Generating Scene "
                f"{scene_number}..."
            )


            try:

                audio_file = generate_scene_audio(

                    scene_number=scene_number,

                    narration=narration,

                )


                self.state.audio_files.append({

                    "scene_number":
                        scene_number,

                    "audio_file":
                        audio_file,

                })


            except Exception as e:

                # ------------------------------------------
                # DO NOT CRASH ENTIRE PIPELINE
                # ------------------------------------------

                print(
                    f"[Voice Agent] "
                    f"Scene {scene_number} FAILED."
                )

                print(
                    f"[Voice Agent] "
                    f"Error: {e}"
                )

                print(
                    f"[Voice Agent] "
                    f"Continuing to next scene..."
                )


        # ------------------------------------------
        # FINAL SUMMARY
        # ------------------------------------------

        successful = len(
            self.state.audio_files
        )

        failed = (
            len(scenes)
            - successful
        )


        print(
            "\n[Voice Agent] "
            "Voice generation finished."
        )

        print(
            f"[Voice Agent] "
            f"Successful: {successful}"
        )

        print(
            f"[Voice Agent] "
            f"Failed: {failed}"
        )


        return self.state