from research.agent import Agent
from script.agent import ScriptAgent
from storyboard.agent import StoryboardAgent
from voice.agent import VoiceAgent
from media.agent import MediaAgent
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

# ------------------------------------------
# STORYBOARD
# ------------------------------------------

storyboard_agent = StoryboardAgent()


print("\n==============================")
print("STARTING STORYBOARD GENERATION")
print("==============================")


storyboard_state = storyboard_agent.run(

    script=script_state.final_script

)


print("\n==============================")
print("FINAL STORYBOARD")
print("==============================\n")


print(
    f"\nScenes generated: "
    f"{len(storyboard_state.scenes)}"
)


for scene in storyboard_state.scenes:

    print("\n--------------------------")

    print(
        f"SCENE {scene['scene_number']}"
    )

    print(
        f"NARRATION: "
        f"{scene['narration']}"
    )

    print(
        f"VISUAL: "
        f"{scene['visual']}"
    )

    print(
        f"PROMPT: "
        f"{scene['generation_prompt']}"
    )

    print(
        f"DURATION: "
        f"{scene['duration']} seconds"
    )

    print(
        f"TRANSITION: "
        f"{scene.get('transition', 'cut')}"
    )

# ------------------------------------------
# VOICE
# ------------------------------------------

voice_agent = VoiceAgent()


print("\n==============================")
print("STARTING VOICE GENERATION")
print("==============================")


voice_state = voice_agent.run(
    scenes=storyboard_state.scenes
)


print("\n==============================")
print("VOICE GENERATION COMPLETE")
print("==============================\n")


for audio in voice_state.audio_files:

    print(
        f"Scene {audio['scene_number']}: "
        f"{audio['audio_file']}"
    )

media_agent = MediaAgent()

print("\n==============================")
print("STARTING MEDIA GENERATION")
print("==============================")

media_state = media_agent.run(
    storyboard_state.scenes[:3]
)