import difflib


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def baseline_similarity(a: str, b: str) -> float:
    a_norm = _normalize(a)
    b_norm = _normalize(b)
    if not a_norm or not b_norm:
        return 0.0

    return difflib.SequenceMatcher(None, a_norm, b_norm).ratio()


def address_similarity(a: str, b: str) -> float:

    # TODO: implement function to find the best match and return it here
    if not a or not b:
        return 0.0
    return baseline_similarity(a, b)
