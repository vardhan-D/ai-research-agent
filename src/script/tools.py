def format_sources(sources: list) -> str:

    if not sources:
        return "No sources provided."

    formatted = []

    for i, source in enumerate(
        sources,
        1
    ):

        if isinstance(source, dict):

            title = source.get(
                "title",
                "Unknown title"
            )

            url = source.get(
                "url",
                ""
            )

            formatted.append(
                f"{i}. {title} — {url}"
            )

        else:

            formatted.append(
                f"{i}. {source}"
            )

    return "\n".join(
        formatted
    )