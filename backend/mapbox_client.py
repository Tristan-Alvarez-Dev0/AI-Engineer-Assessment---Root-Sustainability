from __future__ import annotations

import os
import httpx
from typing import Optional, List

from dotenv import load_dotenv

load_dotenv()

class MapboxClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("MAPBOX_ACCESS_TOKEN")

        if not self.token:
            raise Exception("MAPBOX_ACCESS_TOKEN must be set")

    def geocode_best_match(self, query: str) -> Optional[str]:
        url = "https://api.mapbox.com/search/geocode/v6/forward"

        # TODO: implement function to find the best match and return it here

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

        # Collect full_address list
        full_addresses: List[str] = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            addr = props.get("full_address")
            if addr:
                full_addresses.append(addr)

        if not full_addresses:
            return None

        return f"Match for {query}"
