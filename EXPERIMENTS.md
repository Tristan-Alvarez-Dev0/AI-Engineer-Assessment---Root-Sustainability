# Address Similarity -- Experiments & Design Decisions

## 1. Problem Framing

The goal of this task is to compute a similarity score between:

-   A raw user-input address
-   The best-matched address returned by Mapbox

The score must:

-   Be in the range `[0.0, 1.0]`
-   Represent how likely both addresses refer to the same real-world
    entity
-   Be robust to formatting differences, spelling variations,
    diacritics, and partial input

The score supports **human review**, not full automation. Therefore,
interpretability and conservative behavior are important.

------------------------------------------------------------------------

## 2. Structured Component Comparison

Addresses are parsed using:

``` python
from postal.parser import parse_address
```

This enables semantic comparison of:

-   `house_number`
-   `road`
-   `postcode`
-   `city`
-   `state`
-   `country`
-   `house` (POI)
-   `city_district`

### Why this is better

-   Handles reordering naturally
-   Separates strong signals from weak ones
-   Easier to debug and tune
-   More interpretable than black-box models

This became the foundation of the final solution.

------------------------------------------------------------------------

# 3. Final Similarity Design

The final similarity score is composed of three elements:

1.  **Weighted component similarity**
2.  **Coverage penalty**
3.  **Small full-string fuzzy fallback**

------------------------------------------------------------------------

## 3.1 Normalization

Before parsing, both inputs are normalized:

-   Unicode normalization (NFKC)
-   Lowercasing
-   Diacritic stripping (e.g., `Dąbrowskiego → Dabrowskiego`)
-   Punctuation cleanup
-   Whitespace normalization

This improves:

-   Parsing quality
-   Fuzzy similarity consistency
-   Cross-language robustness

------------------------------------------------------------------------

## 3.2 Weighted Component Matching

Each address component is assigned a weight reflecting importance:


| Component        | Weight |
|------------------|--------|
| house_number     | 0.30   |
| road             | 0.35   |
| postcode         | 0.15   |
| city             | 0.10   |
| state            | 0.05   |
| country          | 0.05   |
| house (POI)      | 0.03   |
| city_district    | 0.02   |

### Rationale

-   Street + house number are strongest indicators.
-   Postcode is strong but not always present.
-   Country alone is weak.
-   POI/building names provide signal but are secondary.

# 4. What I Would Explore Next

1.  **Country Canonicalization**\
    Map ISO codes and language variants to canonical names.

2.   **Geographic Distance Penalty**\
    Use Mapbox coordinates to compute distance and penalize large spatial separation.

3.   **Learned Weight Calibration**\
    Use labeled examples to learn optimal weights rather than fixed
    heuristics.
5. **Embeddings**\
    Use embeddings to have a more robust approch for string matching using dot product


------------------------------------------------------------------------

# 5. Final Thoughts

The implemented solution balances:

-   Interpretability
-   Practical robustness
-   Runtime efficiency
-   Tunability

It avoids:

-   Overconfidence from weak overlap
-   Over-penalizing incomplete input

Most importantly, it supports the product goal:

> Surface low-confidence matches for human review while avoiding
> unnecessary manual checks.

The system is explainable, debuggable, and production-friendly.

