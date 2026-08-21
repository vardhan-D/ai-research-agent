from storyboard.agent import StoryboardAgent


script = """
Imagine a world where robots work alongside humans.

Robots are increasingly used in manufacturing.
They can assemble products, work in hazardous environments,
and perform repetitive tasks.

Artificial intelligence is also making robots smarter.
AI allows robots to recognize patterns, plan tasks,
and collaborate with humans.

Collaborative robots, also called cobots,
are designed specifically to work safely alongside people.

The future of robotics will combine automation,
artificial intelligence, and human collaboration.
"""


agent = StoryboardAgent()


state = agent.run(
    script=script
)


print(
    "\nScenes generated:",
    len(state.scenes)
)


for scene in state.scenes:

    print(
        scene[
            "scene_number"
        ],
        scene[
            "narration"
        ]
    )