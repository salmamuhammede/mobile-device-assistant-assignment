# Standard library

# Third-party
import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

# Local
from app.configs.config import EMBEDDING_MODEL_NAME
from app.data.devices import DEVICE_DOCUMENTS


class EmbeddingModel:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        logger.info("Loading embedding model: {}", model_name)

        self.model = SentenceTransformer(model_name)

        logger.success("Embedding model loaded successfully.")

    def encode_documents(self, documents: list[str]) -> np.ndarray:
        """Encode documents into normalized dense embeddings."""
        logger.info("Encoding {} documents...", len(documents))

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        )

        logger.success("Documents encoded successfully.")

        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a query into a normalized dense embedding."""
        logger.info("Encoding query...")

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        logger.success("Query encoded successfully.")

        return embedding

    def search(
        self,
        query: str,
        documents: list[str],
    ) -> list[int]:
        """Return document indices ordered by cosine similarity."""
        logger.info("Running dense search...")

        document_embeddings = self.encode_documents(documents)
        query_embedding = self.encode_query(query)

        # Since embeddings are normalized,
        # dot product is equivalent to cosine similarity.
        scores = np.dot(document_embeddings, query_embedding)

        ranked_indices = np.argsort(scores)[::-1].tolist()

        logger.success("Dense search completed.")

        return ranked_indices


def main():
    logger.info("Testing embeddings...")

    query = "best phone for low light photography"

    embedding_model = EmbeddingModel()

    results = embedding_model.search(query, DEVICE_DOCUMENTS)

    print("\nDense ranking:")

    for rank, index in enumerate(results, start=1):
        print(f"{rank}. {DEVICE_DOCUMENTS[index]}")


if __name__ == "__main__":
    main()
