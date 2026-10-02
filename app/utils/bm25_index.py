# Standard library

# Third-party
from loguru import logger
from rank_bm25 import BM25Okapi

# Local
from app.data.devices import DEVICE_DOCUMENTS


class BM25Index:
    def __init__(self, documents: list[str]):
        logger.info("Building BM25 index...")

        self.documents = documents
        tokenized_documents = [document.lower().split() for document in documents]

        self.bm25 = BM25Okapi(tokenized_documents)

        logger.success("BM25 index built successfully.")

    def search(self, query: str) -> list[int]:
        """Return document indices ordered by BM25 relevance."""
        logger.info("Running BM25 search...")

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        logger.success("BM25 search completed.")

        return ranked_indices


def main():
    logger.info("Testing bm25_index ...")
    index = BM25Index(DEVICE_DOCUMENTS)

    query = "best phone for low light photography"

    results = index.search(query)

    print("\nBM25 ranking:")

    for rank, index in enumerate(results, start=1):
        print(f"{rank}. {DEVICE_DOCUMENTS[index]}")


if __name__ == "__main__":
    main()
