# Standard library
from typing import Literal

from loguru import logger

# Third-party
from pydantic import BaseModel, Field


class Device(BaseModel):
    brand: str
    model: str
    specs: dict[str, str]
    release_year: int
    price_tier: Literal["budget", "mid-range", "flagship"]


class ExtractRequest(BaseModel):
    text: str = Field(..., max_length=500)


class ExtractResponse(BaseModel):
    brand: str
    model: str
    specs: dict[str, str]
    release_year: int
    price_tier: Literal["budget", "mid-range", "flagship"]


class SearchRequest(BaseModel):
    q: str = Field(..., max_length=500)


class SearchResult(BaseModel):
    document: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]


def main():
    logger.info("Testing device validation")
    device = Device(
        brand="Samsung",
        model="Galaxy S24 Ultra",
        specs={
            "display": "6.8 inch Dynamic AMOLED",
            "battery": "5000 mAh",
            "camera": "200MP",
        },
        release_year=2024,
        price_tier="flagship",
    )

    print(device)


if __name__ == "__main__":
    main()
