import os
import asyncio

import edge_tts


OUTPUT_DIR = "output/audio"


async def generate_audio(
    text: str,
    output_file: str,
    voice: str = "en-US-GuyNeural",
    max_retries: int = 3,
):

    # ------------------------------------------
    # TRY GENERATING AUDIO
    # ------------------------------------------

    for attempt in range(
        1,
        max_retries + 1
    ):

        try:

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
            )

            await communicate.save(
                output_file
            )

            return


        except Exception as e:

            print(
                f"[Voice Tool] "
                f"Attempt {attempt}/"
                f"{max_retries} failed."
            )

            print(
                f"[Voice Tool] Error: {e}"
            )


            # ------------------------------------------
            # STOP AFTER FINAL ATTEMPT
            # ------------------------------------------

            if attempt == max_retries:

                raise


            # ------------------------------------------
            # WAIT BEFORE RETRYING
            # ------------------------------------------

            print(
                "[Voice Tool] "
                "Waiting 3 seconds before retry..."
            )

            wait_time = attempt * 5

            print(
                f"[Voice Tool] "
                f"Waiting {wait_time} seconds "
                f"before retry..."
            )

            await asyncio.sleep(
                wait_time
            )


def generate_scene_audio(
    scene_number: int,
    narration: str,
):

    # ------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # ------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    # ------------------------------------------
    # CREATE OUTPUT FILE PATH
    # ------------------------------------------

    output_file = os.path.join(

        OUTPUT_DIR,

        f"scene_{scene_number:03d}.mp3"

    )


    # ------------------------------------------
    # SKIP IF AUDIO ALREADY EXISTS
    # ------------------------------------------

    if os.path.exists(
        output_file
    ):

        print(
            f"[Voice Tool] "
            f"Scene {scene_number} "
            f"already exists. Skipping."
        )

        return output_file


    # ------------------------------------------
    # GENERATE AUDIO
    # ------------------------------------------

    print(
        f"[Voice Tool] "
        f"Generating audio for "
        f"scene {scene_number}..."
    )


    asyncio.run(

        generate_audio(

            text=narration,

            output_file=output_file,

        )

    )


    print(
        f"[Voice Tool] "
        f"Scene {scene_number} "
        f"saved to {output_file}"
    )


    return output_file