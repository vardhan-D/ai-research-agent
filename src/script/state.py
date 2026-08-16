from dataclasses import dataclass, field


@dataclass
class ScriptState:

    topic: str

    research: str = ""

    sources: list = field(
        default_factory=list
    )

    draft: str = ""

    final_script: str = ""

    title: str = ""

    description: str = ""

    script_valid: bool = False