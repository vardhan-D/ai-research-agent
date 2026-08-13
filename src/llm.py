from ollama import Client
from prompts import SYSTEM_PROMPT
from tools import TOOLS

class LLM:
    def __init__(self):
        self.client = Client()
        self.model = "llama3.2"

    def chat(self, messages, tools=None):
        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=TOOLS
        )

        return response