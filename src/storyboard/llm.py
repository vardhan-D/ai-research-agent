from ollama import Client


STORYBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_number": {
                        "type": "integer"
                    },
                    "narration": {
                        "type": "string"
                    },
                    "visual": {
                        "type": "string"
                    },
                    "generation_prompt": {
                        "type": "string"
                    },
                    "duration": {
                        "type": "number"
                    },
                    "transition": {
                        "type": "string",
                        "enum": [
                            "cut",
                            "fade",
                            "dissolve"
                        ]
                    }
                },
                "required": [
                    "scene_number",
                    "narration",
                    "visual",
                    "generation_prompt",
                    "duration",
                    "transition"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "scenes"
    ],
    "additionalProperties": False
}


class StoryboardLLM:

    def __init__(self):

        self.client = Client(
            timeout=180
        )

        self.model = "llama3.2"


    def generate(
        self,
        system_prompt,
        user_prompt
    ):

        print(
            "[Storyboard LLM] "
            "Sending request to Ollama..."
        )


        response = self.client.chat(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],

            # ------------------------------------------
            # FORCE STRUCTURED JSON
            # ------------------------------------------

            format=STORYBOARD_SCHEMA,


            # ------------------------------------------
            # LOW TEMPERATURE = MORE CONSISTENT OUTPUT
            # ------------------------------------------

            options={
                "temperature": 0
            },

        )


        print(
            "[Storyboard LLM] "
            "Response received from Ollama."
        )


        return response.message.content