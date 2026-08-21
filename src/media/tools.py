import os
import time
import base64

import requests
from dotenv import load_dotenv


load_dotenv()


OUTPUT_DIR = "output/images"

MODEL = "@cf/black-forest-labs/flux-2-klein-4b"


def generate_image(
    prompt: str,
    scene_number: int,
    max_retries: int = 3,
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

        f"scene_{scene_number:03d}.png"

    )


    # ------------------------------------------
    # SKIP IF IMAGE ALREADY EXISTS
    # ------------------------------------------

    if os.path.exists(
        output_file
    ):

        print(
            f"[Media Tool] "
            f"Scene {scene_number} "
            f"already exists. Skipping."
        )

        return output_file


    # ------------------------------------------
    # GET CLOUDFLARE CREDENTIALS
    # ------------------------------------------

    account_id = os.getenv(
        "CLOUDFLARE_ACCOUNT_ID"
    )

    api_token = os.getenv(
        "CLOUDFLARE_API_TOKEN"
    )


    if not account_id:

        raise ValueError(
            "CLOUDFLARE_ACCOUNT_ID "
            "not found in .env"
        )


    if not api_token:

        raise ValueError(
            "CLOUDFLARE_API_TOKEN "
            "not found in .env"
        )


    # ------------------------------------------
    # BUILD API URL
    # ------------------------------------------

    url = (
        "https://api.cloudflare.com/"
        "client/v4/accounts/"
        f"{account_id}/ai/run/"
        f"{MODEL}"
    )


    # ------------------------------------------
    # AUTHENTICATION
    # ------------------------------------------

    headers = {

        "Authorization":
            f"Bearer {api_token}"

    }


    # ------------------------------------------
    # IMAGE GENERATION INPUT
    # ------------------------------------------

    data = {

        "prompt": prompt,

        "width": "1024",

        "height": "576",

    }


    # ------------------------------------------
    # RETRY LOOP
    # ------------------------------------------

    for attempt in range(
        1,
        max_retries + 1
    ):

        try:

            print(
                f"[Media Tool] "
                f"Requesting image for "
                f"scene {scene_number} "
                f"(attempt {attempt}/"
                f"{max_retries})..."
            )


            response = requests.post(

                url,

                headers=headers,

                files={
                    key: (
                        None,
                        value
                    )
                    for key, value
                    in data.items()
                },

                timeout=90

            )


            # ------------------------------------------
            # CHECK HTTP RESPONSE
            # ------------------------------------------

            if not response.ok:

                print(
                    f"[Media Tool] "
                    f"Cloudflare returned "
                    f"status "
                    f"{response.status_code}."
                )

                print(
                    f"[Media Tool] "
                    f"Response: "
                    f"{response.text[:500]}"
                )


                response.raise_for_status()


            # ------------------------------------------
            # READ RESPONSE JSON
            # ------------------------------------------

            response_data = (
                response.json()
            )


            image_base64 = (
                response_data
                .get("result", {})
                .get("image")
            )


            if not image_base64:

                raise ValueError(
                    "Cloudflare response "
                    "did not contain image data."
                )


            # ------------------------------------------
            # DECODE IMAGE
            # ------------------------------------------

            image_bytes = (
                base64.b64decode(
                    image_base64
                )
            )


            # ------------------------------------------
            # SAVE IMAGE
            # ------------------------------------------

            with open(
                output_file,
                "wb"
            ) as file:

                file.write(
                    image_bytes
                )


            print(
                f"[Media Tool] "
                f"Image saved to "
                f"{output_file}"
            )


            return output_file


        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException,
            ValueError
        ) as e:

            print(
                f"[Media Tool] "
                f"Scene {scene_number} "
                f"attempt {attempt}/"
                f"{max_retries} failed."
            )

            print(
                f"[Media Tool] "
                f"Error: {e}"
            )


            if attempt == max_retries:

                raise


            wait_time = attempt * 5


            print(
                f"[Media Tool] "
                f"Waiting {wait_time} "
                f"seconds before retry..."
            )


            time.sleep(
                wait_time
            )