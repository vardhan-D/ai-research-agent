from agent import Agent


agent = Agent()

prompt = input("Combine 'Artificial' and 'Intelligence' to form a new word.")

response = agent.run(prompt)

print("\nFinal Answer:\n")
print(response)