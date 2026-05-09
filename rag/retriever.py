import json
import logging
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TOTAL_SHARDS = 20
TOP_K_PER_SHARD = 3
FINAL_TOP_K = 6
EMBEDDING_DIMENSION = 384


def load_embedding_model() -> SentenceTransformer:
    """Load embedding model."""

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def embed_query(model: SentenceTransformer, query: str) -> np.ndarray:
    """Convert user query into embedding."""

    embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(embedding)

    return embedding


def load_shard_index(shard_number: int):
    """Load FAISS shard index."""

    index_path = f"rag/indexes/shard_{shard_number}.index"

    index = faiss.read_index(index_path)

    return index


def load_shard_metadata(shard_number: int) -> list:
    """Load shard metadata."""

    metadata_path = f"rag/metadata/shard_{shard_number}.json"

    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return metadata


def search_single_shard(
    shard_number: int,
    query_embedding: np.ndarray
) -> list:
    """Search one shard."""

    index = load_shard_index(shard_number)
    metadata = load_shard_metadata(shard_number)

    scores, indices = index.search(query_embedding, TOP_K_PER_SHARD)

    candidates = []

    for score, index_position in zip(scores[0], indices[0]):
        if index_position == -1:
            continue

        item = metadata[index_position]

        candidates.append({
            "show_id": item["show_id"],
            "title": item["title"],
            "text": item["text"],
            "score": float(score)
        })

    return candidates


def search_all_shards(
    query_embedding: np.ndarray
) -> list:
    """Search all shards in parallel."""

    all_candidates = []

    with ThreadPoolExecutor(max_workers=TOTAL_SHARDS) as executor:
        futures = []

        for shard_number in range(TOTAL_SHARDS):
            future = executor.submit(
                search_single_shard,
                shard_number,
                query_embedding
            )
            futures.append(future)

        for future in futures:
            shard_candidates = future.result()
            all_candidates.extend(shard_candidates)

    return all_candidates


def rerank_candidates(candidates: list) -> list:
    """Sort candidates by similarity score."""

    sorted_candidates = sorted(
        candidates,
        key=lambda item: item["score"],
        reverse=True
    )

    return sorted_candidates[:FINAL_TOP_K]


def retrieve_top_chunks(query: str) -> list:
    """Retrieve best chunks for user query."""

    model = load_embedding_model()

    query_embedding = embed_query(model, query)

    candidates = search_all_shards(query_embedding)

    top_chunks = rerank_candidates(candidates)

    return top_chunks


def main() -> None:
    """Test retrieval pipeline."""

    query = "Suggest comedy movies from India with strong female lead"

    results = retrieve_top_chunks(query)

    logger.info("TOP RETRIEVED CHUNKS")

    for item in results:
        logger.info(f"Title: {item['title']}")
        logger.info(f"Show ID: {item['show_id']}")
        logger.info(f"Score: {item['score']}")
        logger.info("-" * 50)


if __name__ == "__main__":
    main()