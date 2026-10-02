# Standard library

# Third-party
from loguru import logger

# Local
from app.data.devices import DEVICE_DOCUMENTS
from app.utils.bm25_index import BM25Index
from app.utils.embeddings import EmbeddingModel

RRF_K = 60


class HybridSearch:
    def __init__(self, documents: list[str]):
        logger.info("Initializing hybrid search...")

        self.documents = documents

        # Build the BM25 index once.
        self.bm25_index = BM25Index(documents)

        # Load the embedding model once.
        self.embedding_model = EmbeddingModel()

        logger.success("Hybrid search initialized successfully.")

    def rrf(
        self,
        sparse_ranking: list[int],
        dense_ranking: list[int],
    ) -> list[tuple[int, float]]:
        """Fuse sparse and dense rankings using Reciprocal Rank Fusion."""

        logger.info("Applying Reciprocal Rank Fusion...")

        rrf_scores = {}

        # BM25 ranking
        for rank, document_index in enumerate(sparse_ranking, start=1):
            rrf_scores[document_index] = rrf_scores.get(document_index, 0.0) + 1 / (
                RRF_K + rank
            )

        # Dense ranking
        for rank, document_index in enumerate(dense_ranking, start=1):
            rrf_scores[document_index] = rrf_scores.get(document_index, 0.0) + 1 / (
                RRF_K + rank
            )

        ranked_results = sorted(
            rrf_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        logger.success("RRF completed successfully.")

        return ranked_results

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[str, float]]:
        """Run hybrid search and return the top-k documents."""

        logger.info("Running hybrid search for query: {}", query)

        # Get rankings from both retrieval methods.
        sparse_ranking = self.bm25_index.search(query)

        dense_ranking = self.embedding_model.search(
            query,
            self.documents,
        )

        # Fuse both rankings.
        fused_results = self.rrf(
            sparse_ranking,
            dense_ranking,
        )

        # Convert document indices to actual documents.
        results = [
            (self.documents[index], score) for index, score in fused_results[:top_k]
        ]

        logger.success(
            "Hybrid search completed. Returned {} results.",
            len(results),
        )

        return results


def main():
    logger.info("Testing hybrid search...")

    search_engine = HybridSearch(DEVICE_DOCUMENTS)

    query = "best phone for low light photography"

    results = search_engine.search(
        query=query,
        top_k=3,
    )

    print("\nHybrid Search Results:")

    for rank, (document, score) in enumerate(results, start=1):
        print(f"{rank}. Score: {score:.6f}")
        print(f"   {document}")


if __name__ == "__main__":
    main()
