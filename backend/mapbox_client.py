from __future__ import annotations

import os
from typing import Optional

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

        return f"Match for {query}"
