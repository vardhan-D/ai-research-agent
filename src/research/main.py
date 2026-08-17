from .agent import Agent


agent = Agent()


print(
    "Ask the research agent: "
)


prompt = input()


response = agent.run(
    prompt
)


print(
    "\nFinal Answer:\n"
)


print(
    response
)


print(
    "\nResearch State:\n"
)


print(
    agent.state
)