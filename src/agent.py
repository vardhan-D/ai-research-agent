from llm import LLM
from tools import add_strings
from prompts import SYSTEM_PROMPT

TOOLS = {
    "add_strings": add_strings,
}


class Agent:

    def __init__(self):
        self.llm = LLM()

    def run(self, prompt):

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        while True:

            response = self.llm.chat(
                messages=messages,
                tools=list(TOOLS.values()),
            )

            # Save the assistant's response
            messages.append(response.message)

            # No tool requested
            if not response.message.tool_calls:
                return response.message.content

            # Execute requested tools
            for tool_call in response.message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                tool_function = TOOLS.get(tool_name)

                if tool_function is None:
                    raise ValueError(
                        f"Unknown tool requested: {tool_name}"
                    )

                result = tool_function(**arguments)

                print(
                    f"[Tool] {tool_name}({arguments}) -> {result}"
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                    }
                )
