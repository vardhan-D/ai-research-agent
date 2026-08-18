import os

import requests
from dotenv import load_dotenv
import base64

load_dotenv()


OUTPUT_DIR = "output/images"

MODEL = "@cf/black-forest-labs/flux-2-klein-4b"


def generate_image(
    prompt: str,
    scene_number: int
):

    # ------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # ------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


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


    print(
        f"[Media Tool] "
        f"Requesting image for "
        f"scene {scene_number}..."
    )


    # ------------------------------------------
    # CALL CLOUDFLARE
    # ------------------------------------------

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

        timeout=120

    )


    # ------------------------------------------
    # CHECK FOR ERRORS
    # ------------------------------------------

    if not response.ok:

        print(
            "[Media Tool] "
            "Cloudflare request failed."
        )

        print(
            f"Status code: "
            f"{response.status_code}"
        )

        print(
            f"Response: "
            f"{response.text}"
        )

        response.raise_for_status()


    # ------------------------------------------
    # READ CLOUDFLARE RESPONSE
    # ------------------------------------------

    response_data = response.json()


    image_base64 = (
        response_data
        .get("result", {})
        .get("image")
    )


    if not image_base64:

        raise ValueError(
            "Cloudflare response did not contain image data."
        )


    # ------------------------------------------
    # DECODE BASE64 IMAGE
    # ------------------------------------------

    image_bytes = base64.b64decode(
        image_base64
    )


    # ------------------------------------------
    # SAVE IMAGE
    # ------------------------------------------

    output_file = os.path.join(

        OUTPUT_DIR,

        f"scene_{scene_number:03d}.png"

    )


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