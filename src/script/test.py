from .agent import ScriptAgent


agent = ScriptAgent()


research = """
Humanoid robotics is rapidly developing.

Recent developments include improvements
in humanoid locomotion, manipulation,
computer vision, AI-based control systems,
and the use of robots in industrial
environments.

Several companies and research groups are
working on increasingly capable humanoid
robots.

The research indicates that robotics is
increasingly combining physical hardware
with modern AI models.
"""


sources = [

    {
        "title": "Robotics Research Source",
        "url": "https://example.com/robotics",
    },

    {
        "title": "Robotics Industry Report",
        "url": "https://example.com/robotics-report",
    },

]


state = agent.run(

    topic=
        "Latest developments in humanoid robotics",

    research=
        research,

    sources=
        sources,
)


print(
    "\n=============================="
)

print(
    "GENERATED SCRIPT"
)

print(
    "==============================\n"
)

print(
    state.final_script
)