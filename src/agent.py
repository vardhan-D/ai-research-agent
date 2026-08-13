from llm import LLM
from prompts import SYSTEM_PROMPT
from tools import TOOLS, TOOL_MAP


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
                tools=TOOLS
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

                print(f"\n[Agent] Tool requested: {tool_name}")
                print(f"[Agent] Arguments: {arguments}")

                tool_function = TOOL_MAP.get(tool_name)

                if tool_function is None:
                    raise ValueError(
                        f"Unknown tool requested: {tool_name}"
                    )

                # Python actually executes the function here
                result = tool_function(**arguments)

                print(
                    f"[Tool Result] {result}"
                )

                # Give the tool result back to the LLM
                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                    }
                )