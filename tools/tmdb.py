import os
from typing import Literal

import httpx
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

TMDB_API_KEY = os.getenv("TMDB_API_KEY")


class TrendingMoviesInput(BaseModel):
    time_period: Literal["day", "week"] = Field(
        "day",
        description="The time period for which to get the trending movies. Defaults to 'day' if not clear.",
        required=False,
    )


@tool
def get_current_trending_movies(
    time_period: Literal["day", "week"] = "day",
) -> list[dict[str, any]] | str:
    """Returns the current trending movies."""
    url = f"https://api.themoviedb.org/3/trending/movie/{time_period}"
    response = httpx.get(url, headers={"Authorization": f"Bearer {TMDB_API_KEY}"})
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        return str(e)
    return response.json()["results"]
