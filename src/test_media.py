from storyboard.agent import StoryboardAgent
from voice.agent import VoiceAgent
from media.agent import MediaAgent


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


# ------------------------------------------
# STORYBOARD
# ------------------------------------------

storyboard_agent = StoryboardAgent()

storyboard_state = storyboard_agent.run(
    script=script
)


print(
    f"\nStoryboard scenes: "
    f"{len(storyboard_state.scenes)}"
)


if not storyboard_state.scenes:

    raise RuntimeError(
        "Storyboard generated 0 scenes."
    )


# ------------------------------------------
# VOICE TEST
# ------------------------------------------

print(
    "\n=============================="
)

print(
    "TESTING VOICE AGENT"
)

print(
    "=============================="
)


voice_agent = VoiceAgent()

voice_state = voice_agent.run(

    # Only test first 2 scenes for now
    scenes=storyboard_state.scenes[:2]

)


# ------------------------------------------
# MEDIA TEST
# ------------------------------------------

print(
    "\n=============================="
)

print(
    "TESTING MEDIA AGENT"
)

print(
    "=============================="
)


media_agent = MediaAgent()

media_state = media_agent.run(

    # Only test first 2 scenes for now
    scenes=storyboard_state.scenes[:2]

)


# ------------------------------------------
# RESULTS
# ------------------------------------------

print(
    "\n=============================="
)

print(
    "TEST RESULTS"
)

print(
    "=============================="
)


print(
    f"Voice outputs: "
    f"{len(voice_state.audio_files)}"
)


print(
    f"Media outputs: "
    f"{len(media_state.generated_media)}"
)