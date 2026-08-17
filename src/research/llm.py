from ollama import Client

from .tools import TOOLS


class LLM:

    def __init__(self):

        self.client = Client()

        self.model = "llama3.2"


    def chat(
        self,
        messages,
        tools=None
    ):

        if tools is None:

            tools = []


        response = self.client.chat(

            model=self.model,

            messages=messages,

            tools=tools,
        )


        return response