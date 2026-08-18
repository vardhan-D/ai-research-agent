from .state import MediaState
from .tools import generate_image


class MediaAgent:

    def __init__(self):

        self.state = None


    def run(
        self,
        scenes: list
    ):

        # ------------------------------------------
        # CREATE STATE
        # ------------------------------------------

        self.state = MediaState(

            scenes=scenes

        )


        print(
            "\n[Media Agent] "
            "Generating images..."
        )


        # ------------------------------------------
        # GENERATE IMAGE FOR EACH SCENE
        # ------------------------------------------

        for scene in scenes:

            scene_number = scene.get(
                "scene_number"
            )

            generation_prompt = scene.get(
                "generation_prompt",
                ""
            )


            if not generation_prompt:

                print(
                    f"[Media Agent] "
                    f"Skipping scene "
                    f"{scene_number}: "
                    f"no generation prompt."
                )

                continue


            try:

                print(
                    f"\n[Media Agent] "
                    f"Scene {scene_number}"
                )


                image_path = generate_image(

                    prompt=generation_prompt,

                    scene_number=scene_number

                )


                media_item = {

                    "scene_number":
                        scene_number,

                    "image_path":
                        image_path,

                    "generation_prompt":
                        generation_prompt,

                }


                self.state.generated_media.append(
                    media_item
                )


            except Exception as e:

                print(
                    f"[Media Agent] "
                    f"Scene {scene_number} "
                    f"failed: {e}"
                )


        print(
            "\n[Media Agent] "
            f"Finished generating "
            f"{len(self.state.generated_media)} "
            f"images."
        )


        return self.state