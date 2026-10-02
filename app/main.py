# Third-party
from fastapi import FastAPI, HTTPException
from loguru import logger

from app.data.devices import DEVICE_DOCUMENTS

# Local
from app.schema.device import (
    Device,
    ExtractRequest,
    ExtractResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.extraction import extract_device
from app.services.search import HybridSearch

app = FastAPI(
    title="Mobile Device Assistant API",
    description="API for mobile device extraction and hybrid search.",
    version="1.0.0",
)


# Initialize hybrid search once when the application starts.
search_engine = HybridSearch(DEVICE_DOCUMENTS)


@app.get("/")
def root():
    return {"message": "Mobile Device Assistant API is running."}


@app.post("/extract", response_model=ExtractResponse)
def extract_device_endpoint(request: ExtractRequest):
    """Extract structured mobile device information from text."""

    logger.info("Received extraction request.")

    try:
        device: Device = extract_device(request.text)

        return ExtractResponse(**device.model_dump())

    except ValueError as exc:
        logger.warning("Extraction request rejected: {}", exc)

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected extraction error.")

        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        ) from exc


@app.post("/search", response_model=SearchResponse)
def search_devices(request: SearchRequest):
    """Search the device catalog using hybrid retrieval."""

    logger.info("Received search request.")

    try:
        results = search_engine.search(
            query=request.q,
            top_k=3,
        )

        return SearchResponse(
            results=[
                SearchResult(
                    document=document,
                    score=score,
                )
                for document, score in results
            ]
        )

    except Exception as exc:
        logger.exception("Unexpected search error.")

        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        ) from exc
