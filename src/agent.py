from llm import LLM
from prompts import SYSTEM_PROMPT

from tools import TOOLS, TOOL_MAP

from state import ResearchState


class Agent:

    def __init__(self):

        self.llm = LLM()

        # State belongs to the agent,
        # NOT to the LLM.
        self.state = None


    def run(self, prompt):

        # --------------------------------------------------
        # CREATE RESEARCH STATE
        # --------------------------------------------------

        self.state = ResearchState(
            query=prompt
        )


        # --------------------------------------------------
        # INITIAL CONVERSATION
        # --------------------------------------------------

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


        # --------------------------------------------------
        # AGENT LOOP
        # --------------------------------------------------

        while True:

            response = self.llm.chat(
                messages=messages,
                tools=TOOLS,
            )


            # --------------------------------------------------
            # SAVE ASSISTANT RESPONSE
            # --------------------------------------------------

            messages.append(
                response.message
            )


            # --------------------------------------------------
            # NO TOOL REQUESTED
            # --------------------------------------------------

            if not response.message.tool_calls:

                return response.message.content


            # --------------------------------------------------
            # EXECUTE TOOL CALLS
            # --------------------------------------------------

            for tool_call in response.message.tool_calls:

                tool_name = (
                    tool_call.function.name
                )

                arguments = (
                    tool_call.function.arguments
                )


                print(
                    f"\n[Agent] Tool requested: "
                    f"{tool_name}"
                )

                print(
                    f"[Agent] Arguments: "
                    f"{arguments}"
                )


                # --------------------------------------------------
                # FIND PYTHON FUNCTION
                # --------------------------------------------------

                tool_function = TOOL_MAP.get(
                    tool_name
                )


                if tool_function is None:

                    raise ValueError(
                        f"Unknown tool requested: "
                        f"{tool_name}"
                    )


                # --------------------------------------------------
                # EXECUTE TOOL
                # --------------------------------------------------
                #
                # Only research_web receives state.
                #
                # The LLM does NOT provide state.
                #
                # The agent injects it here.
                # --------------------------------------------------

                if tool_name in ["research_web", "synthesize_research"]:

                    result = tool_function(
                        state=self.state,
                        **arguments,
                    )

                else:

                    result = tool_function(
                        **arguments
                    )


                # --------------------------------------------------
                # PRINT TOOL RESULT
                # --------------------------------------------------

                print(
                    f"\n[Tool Result] "
                    f"{result}"
                )


                # --------------------------------------------------
                # SEND TOOL RESULT BACK TO LLM
                # --------------------------------------------------

                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                    }
                )