def rerank_results(results: list[dict]) -> list[dict]:
    """
    Base version:
    Chroma already returns semantic ranking.

    Advanced version later:
    - add git last modified date
    - add symbol name boost
    - add exact keyword boost
    """

    return sorted(
        results,
        key=lambda item: item.get("score", 0),
        reverse=True,
    )