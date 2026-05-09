import os
import json
import logging
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TOTAL_SHARDS = 20
EMBEDDING_DIMENSION = 384


def load_chunks(chunks_path: str) -> list:
    """Load chunk data from JSON file."""

    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    return chunks


def split_into_shards(chunks: list, total_shards: int) -> list:
    """Split chunks into equal shards."""

    shard_size = len(chunks) // total_shards
    shards = []

    for shard_index in range(total_shards):
        start = shard_index * shard_size

        if shard_index == total_shards - 1:
            end = len(chunks)
        else:
            end = start + shard_size

        shards.append(chunks[start:end])

    return shards


def load_embedding_model() -> SentenceTransformer:
    """Load embedding model."""

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def create_embeddings(model: SentenceTransformer, shard: list) -> np.ndarray:
    """Create embeddings for shard text."""

    texts = [item["text"] for item in shard]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings.astype("float32")


def create_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Create cosine similarity FAISS index."""

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    index.add(embeddings)

    return index


def save_faiss_index(index: faiss.Index, output_path: str) -> None:
    """Save FAISS index file."""

    faiss.write_index(index, output_path)


def save_metadata(shard: list, output_path: str) -> None:
    """Save shard metadata."""

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(shard, file, indent=4, ensure_ascii=False)


def create_output_directories() -> None:
    """Create output directories."""

    os.makedirs("rag/indexes", exist_ok=True)
    os.makedirs("rag/metadata", exist_ok=True)


def process_shards(model: SentenceTransformer, shards: list) -> None:
    """Process all shards."""

    for shard_number, shard in enumerate(shards):
        logger.info(f"Processing shard {shard_number + 1}/{TOTAL_SHARDS}")

        embeddings = create_embeddings(model, shard)

        index = create_faiss_index(embeddings)

        index_path = f"rag/indexes/shard_{shard_number}.index"
        metadata_path = f"rag/metadata/shard_{shard_number}.json"

        save_faiss_index(index, index_path)

        save_metadata(shard, metadata_path)

        logger.info(f"Shard {shard_number} completed.")


def main() -> None:
    """Run embedding and indexing pipeline."""

    chunks_path = "rag_data/chunks.json"

    chunks = load_chunks(chunks_path)

    logger.info(f"Total chunks loaded: {len(chunks)}")

    shards = split_into_shards(chunks, TOTAL_SHARDS)

    logger.info(f"Total shards created: {len(shards)}")

    create_output_directories()

    model = load_embedding_model()

    process_shards(model, shards)

    logger.info("All shards processed successfully.")


if __name__ == "__main__":
    main()