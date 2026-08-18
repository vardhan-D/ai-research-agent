from dataclasses import dataclass, field


@dataclass
class StoryboardState:

    script: str

    scenes: list = field(
        default_factory=list
    )

    final_storyboard: str = ""