from ollama import Client


class ScriptLLM:

    def __init__(self):

        self.client = Client()

        self.model = "llama3.2"


    def generate(
        self,
        system_prompt,
        user_prompt
    ):

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
        )

        return response.message.content