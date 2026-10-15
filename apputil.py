import os

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()


class Genius:
    """Class for collecting artist information from the Genius API."""

    def __init__(self, access_token=None):
        """Initialize the Genius API client."""
        if access_token is None:
            access_token = os.environ.get("ACCESS_TOKEN")

        self.access_token = access_token
        self.base_url = "https://api.genius.com"

    def _get_json(self, path, params=None):
        """Send a request to Genius and return JSON data."""
        if params is None:
            params = {}
        else:
            params = params.copy()

        params["access_token"] = self.access_token

        response = requests.get(
            f"{self.base_url}{path}",
            params=params
        )

        response.raise_for_status()

        return response.json()

    def _search(self, search_term):
        """Search Genius for a term."""
        return self._get_json(
            "/search",
            params={"q": search_term}
        )

    def _get_artist_id(self, search_term):
        """Get the primary artist ID from the first search result."""
        json_data = self._search(search_term)

        first_hit = json_data["response"]["hits"][0]

        return first_hit["result"]["primary_artist"]["id"]

    def get_artist(self, search_term):
        """Return the full JSON result for an artist."""
        artist_id = self._get_artist_id(search_term)

        return self._get_json(
            f"/artists/{artist_id}"
        )

    def get_artists(self, search_terms):
        """Return information for multiple artists in a DataFrame."""
        rows = []

        for search_term in search_terms:
            json_data = self.get_artist(search_term)

            artist = json_data["response"]["artist"]

            rows.append({
                "search_term": search_term,
                "artist_name": artist["name"],
                "artist_id": artist["id"],
                "followers_count": artist.get("followers_count")
            })

        return pd.DataFrame(rows)
    