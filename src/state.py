from dataclasses import dataclass, field


@dataclass
class ResearchState:

    query: str

    search_results: list = field(default_factory=list)

    sources_read: list = field(default_factory=list)

    failed_sources: list = field(default_factory=list)

    findings: list = field(default_factory=list)

    gaps: list = field(default_factory=list)

    final_report: str = ""
