from .state import MediaState
from .tools import generate_image


class MediaAgent:

    def __init__(self):

        self.state = None


    def run(
        self,
        scenes: list
    ):

        self.state = MediaState(
            scenes=scenes
        )


        print(
            "\n[Media Agent] "
            "Generating images..."
        )


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
                    f"Scene {scene_number} "
                    f"has no prompt. Skipping."
                )

                continue


            print(
                f"\n[Media Agent] "
                f"Scene {scene_number}"
            )


            try:

                image_path = generate_image(

                    prompt=generation_prompt,

                    scene_number=scene_number,

                )


                self.state.generated_media.append({

                    "scene_number":
                        scene_number,

                    "image_path":
                        image_path,

                    "generation_prompt":
                        generation_prompt,

                })


            except Exception as e:

                print(
                    f"[Media Agent] "
                    f"Scene {scene_number} "
                    f"FAILED."
                )

                print(
                    f"[Media Agent] "
                    f"Error: {e}"
                )

                print(
                    "[Media Agent] "
                    "Continuing to next scene..."
                )


        successful = len(
            self.state.generated_media
        )

        failed = (
            len(scenes)
            - successful
        )


        print(
            "\n[Media Agent] "
            "Media generation finished."
        )

        print(
            f"[Media Agent] "
            f"Successful: {successful}"
        )

        print(
            f"[Media Agent] "
            f"Failed: {failed}"
        )


        return self.state