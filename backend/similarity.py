import difflib
import re
import unicodedata
from typing import Dict, Tuple
from rapidfuzz import fuzz
from pprint import pprint
from postal.parser import parse_address
from dataclasses import dataclass

#========================================================================================
#========================================================================================

@dataclass
class SimilarityResult:
    score: float
    a_components: Dict[str, str]
    b_components: Dict[str, str]
    breakdown: Dict[str, float]


_SPACE_RE = re.compile(r"\s+")
_KEEP_RE = re.compile(r"[^\w\s,/\-]")  # keep word chars, whitespace, comma, slash, hyphen

def info_level(s: str) -> int:
    """
    0 = empty/junk (only whitespace/punctuation after cleaning)
    1 = very low info (single token, no digits)
    2 = medium (2-3 tokens or has digits)
    3 = high (detailed)
    """
    if s is None:
        return 0

    s = str(s).strip()
    if not s:
        return 0

    s2 = re.sub(r"[^\w\s]", " ", s)
    s2 = re.sub(r"\s+", " ", s2).strip()
    if not s2:
        return 0

    toks = [t for t in s2.split(" ") if t]
    has_digit = any(ch.isdigit() for ch in s2)

    if has_digit:
        return 2
    if len(toks) <= 1:
        return 1
    if len(toks) <= 3:
        return 2
    return 3

def strip_diacritics(s: str) -> str:
    nkfd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nkfd if not unicodedata.combining(ch))


def _normalize(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""

    s = unicodedata.normalize("NFKC", s).lower()
    s = strip_diacritics(s)

    s = s.replace("—", "-").replace("–", "-")
    s = _KEEP_RE.sub(" ", s)
    s = re.sub(r"\s*,\s*", ", ", s)
    s = _SPACE_RE.sub(" ", s).strip()
    return s

def _is_short_or_suspicious_road(s: str) -> bool:
    """
    Road like 'az' or very short tokens usually indicates parsing noise (postcode fragment).
    """
    s = (s or "").strip()
    if not s:
        return True
    # If road is super short (<=3 chars) it's likely not a road
    return len(s) <= 3


def _looks_like_postcode_fragment(token: str) -> bool:
    token = (token or "").strip()
    # treat 3-5 digit numeric tokens as postcode-ish fragments
    return token.isdigit() and 3 <= len(token) <= 5


def _clean_house_number(hn: str) -> str:
    """
    Fix libpostal anomalies like:
    house_number: "202 1014"  (where 1014 is actually postcode fragment)
    Keep first token if multiple tokens and later tokens look like postcode fragments.
    """
    hn = (hn or "").strip()
    if not hn:
        return ""

    toks = hn.split()
    if len(toks) <= 1:
        return hn

    # If any later token looks postcode-ish, keep only first token
    if any(_looks_like_postcode_fragment(t) for t in toks[1:]):
        return toks[0]

    return hn


def _string_fuzzy(a: str, b: str) -> float:
    """
    Lightweight fallback similarity on normalized full strings.
    """
    if not a or not b:
        return 0.0
    return fuzz.token_set_ratio(a, b) / 100.0


def _to_components(parsed: list[Tuple[str, str]]) -> Dict[str, str]:
    """
    libpostal returns: [(value, label), ...]
    We convert to: {label: "joined values"}
    """
    out: Dict[str, list[str]] = {}
    for value, label in parsed:
        out.setdefault(label, []).append(value)
    return {k: " ".join(v) for k, v in out.items()}


def _fuzzy(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.token_set_ratio(a, b) / 100.0


def _exactish(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1.0 if a == b else 0.0


def address_similarity(a: str, b: str) -> SimilarityResult:
    a = "" if a is None else str(a)
    b = "" if b is None else str(b)

    # Normalize before parsing (helps diacritics/punctuation)
    a_norm = _normalize(a)
    b_norm = _normalize(b)

    comp_a = _to_components(parse_address(a_norm))
    comp_b = _to_components(parse_address(b_norm))

    # Weights (importance)
    weights = {
        "house_number": 0.30,
        "road": 0.35,
        "postcode": 0.15,
        "city": 0.10,
        "state": 0.05,
        "country": 0.05,
        "house": 0.03,
        "city_district": 0.02,
    }

    breakdown: Dict[str, float] = {}

    # 1) Similarity computed ONLY on keys present in BOTH
    weighted_sum = 0.0
    common_weight_sum = 0.0

    for key, w in weights.items():
        va = comp_a.get(key, "").strip()
        vb = comp_b.get(key, "").strip()

        # Compare only if BOTH exist
        if not va or not vb:
            continue

        # ---- GUARDS ----
        if key == "house_number":
            va = _clean_house_number(va)
            vb = _clean_house_number(vb)

        if key == "road":
            # If road looks like noise (e.g., "az"), ignore it to avoid false perfect matches
            if _is_short_or_suspicious_road(va) or _is_short_or_suspicious_road(vb):
                continue

        # ---- SCORING ----
        if key in ("house_number", "postcode"):
            s = _exactish(va, vb)
            if s == 0.0 and key == "house_number":
                s = _fuzzy(va, vb)  # "12-A" vs "12A"
        else:
            s = _fuzzy(va, vb)

        breakdown[key] = round(s, 3)
        weighted_sum += w * s
        common_weight_sum += w

    normalized_similarity = (weighted_sum / common_weight_sum) if common_weight_sum > 0 else 0.0

    # 2) Coverage penalty: if one has extra fields the other doesn't, deduct score
    #    Compute coverage over "useful fields that appear in either address"
    union_keys = {k for k in weights if comp_a.get(k) or comp_b.get(k)}
    common_keys = set(breakdown.keys())

    union_weight_sum = sum(weights[k] for k in union_keys) if union_keys else 0.0
    common_keys_weight_sum = sum(weights[k] for k in common_keys) if common_keys else 0.0

    coverage_ratio = (common_keys_weight_sum / union_weight_sum) if union_weight_sum > 0 else 0.0

    component_score = normalized_similarity * coverage_ratio

    # Full-string fuzzy on normalized inputs
    full_fuzzy = _string_fuzzy(a_norm, b_norm)

    # Reduce fuzzy impact for low-info inputs (prevents over-matching on "korea", "porto", etc.)
    lvl_a = info_level(a_norm)
    lvl_b = info_level(b_norm)

    w_fuzzy = 0.15
    if min(lvl_a, lvl_b) <= 1:
        w_fuzzy = 0.05  # very short / vague input => tiny fuzzy influence

    final_score = (1 - w_fuzzy) * component_score + w_fuzzy * full_fuzzy

    result = SimilarityResult(
        score=round(final_score, 3),
        a_components=comp_a,
        b_components=comp_b,
        breakdown={
            **breakdown,
            "component_score": round(component_score, 3),
            "full_fuzzy": round(full_fuzzy, 3),
            "w_fuzzy": round(w_fuzzy, 3),
        },
    )

    pprint(result.__dict__)
    return result
