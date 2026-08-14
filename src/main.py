from agent import Agent


agent = Agent()

prompt = input(
    "Ask the research agent: "
)

response = agent.run(prompt)

print("\nFinal Answer:\n")
print(response)

print("\nResearch State:\n")
print(agent.state)