from dataclasses import dataclass, field


@dataclass
class VoiceState:

    scenes: list

    audio_files: list = field(
        default_factory=list
    )