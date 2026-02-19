from __future__ import annotations
import os
from typing import Optional, List, Dict, Any
import httpx
import json
from dotenv import load_dotenv
from dataclasses import dataclass
from similarity import _normalize
import difflib
load_dotenv()

# =================================================================================
# =================================================================================
# my dataclass

@dataclass
class GeocodeResult:
    matched_address: str
    components: Dict[str, str]
    match_code: Dict[str, str]
    raw: Dict[str, Any]


class MapboxClient:
    def __init__(self, token: str | None = None, timeout: float =1.5) -> None:
        self.token = token or os.getenv("MAPBOX_ACCESS_TOKEN")

        if not self.token:
            raise Exception("MAPBOX_ACCESS_TOKEN must be set")
        self.timeout = timeout

    def geocode_best_match(self, query: str) -> str:
        url = "https://api.mapbox.com/search/geocode/v6/forward"

        # TODO: implement function to find the best match and return it here

        # ============================================================================================
        # ============================================================================================
        # ============================================================================================
        # ============================================================================================


        params = {
            "q": query,
            "access_token": self.token,
            "limit": 5,
            "type": "address, place, locality, region, country, postcode"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                # For debugging

                # print("\nMAPBOX RAW RESPONSE:")
                # print(json.dumps(data, indent=4, ensure_ascii=False))

        except Exception:
            return None


        # =================================================================================
        # =================================================================================

        # Collect full_address list
        full_addresses: List[str] = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            addr = props.get("full_address")
            if addr:
                full_addresses.append(addr)

        if not full_addresses:
            return None

        # Pick best by similarity
        q_norm = _normalize(query)
        best_addr: Optional[str] = None
        best_score = -1.0

        for addr in full_addresses:
            a_norm = _normalize(addr)
            score = difflib.SequenceMatcher(None, q_norm, a_norm).ratio()  # 0..1

            if score > best_score:
                best_score = score
                best_addr = a_norm  # keep ORIGINAL address (not normalized)


        print('\nInput Address: ',q_norm)
        print('ALL Addresses: ',full_addresses)
        print('Length of ALL Addresses: ',len(full_addresses))
        print('BEST Address:', best_addr)
        print('\n')
        return best_addr
