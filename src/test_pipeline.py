from research.agent import Agent
from script.agent import ScriptAgent


# ------------------------------------------
# RESEARCH
# ------------------------------------------

research_agent = Agent()

topic = "What are the latest developments in robotics?"

print("\n==============================")
print("STARTING RESEARCH")
print("==============================")

research_agent.run(topic)


research_state = research_agent.state


print("\n==============================")
print("RESEARCH COMPLETE")
print("==============================")

print(
    f"Findings: {len(research_state.findings)}"
)

print(
    f"Sources: {len(research_state.sources_read)}"
)


# ------------------------------------------
# SCRIPT
# ------------------------------------------

script_agent = ScriptAgent()

print("\n==============================")
print("STARTING SCRIPT GENERATION")
print("==============================")


script_state = script_agent.run_from_research(
    research_state
)


print("\n==============================")
print("FINAL SCRIPT")
print("==============================\n")

print(
    script_state.final_script
)