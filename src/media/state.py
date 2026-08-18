from dataclasses import dataclass, field


@dataclass
class MediaState:

    scenes: list

    generated_media: list = field(
        default_factory=list
    )