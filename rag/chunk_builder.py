import sqlite3
import json
import os


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Create database connection."""

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_titles(connection: sqlite3.Connection) -> list:
    """Fetch all titles from database."""

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM titles")

    rows = cursor.fetchall()

    return rows


def build_chunk(row: sqlite3.Row) -> dict:
    """Convert database row into RAG chunk."""

    chunk_text = f"""
Show ID: {row["show_id"]}
Title: {row["title"]}
Type: {row["type"]}
Director: {row["director"]}
Cast: {row["cast"]}
Country: {row["country"]}
Release Year: {row["release_year"]}
Rating: {row["rating"]}
Duration: {row["duration"]}
Genres: {row["listed_in"]}
Description: {row["description"]}
""".strip()

    return {
        "show_id": row["show_id"],
        "title": row["title"],
        "text": chunk_text
    }


def build_all_chunks(rows: list) -> list:
    """Build chunks for all titles."""

    chunks = []

    for row in rows:
        chunk = build_chunk(row)
        chunks.append(chunk)

    return chunks


def save_chunks(chunks: list, output_path: str) -> None:
    """Save chunks to JSON file."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)


def main() -> None:
    """Run chunk building pipeline."""

    db_path = "data/netflix.db"
    output_path = "rag_data/chunks.json"

    connection = get_db_connection(db_path)

    rows = fetch_titles(connection)

    chunks = build_all_chunks(rows)

    save_chunks(chunks, output_path)

    connection.close()

    print(f"Total rows fetched: {len(rows)}")
    print(f"Total chunks created: {len(chunks)}")
    print("Chunk file saved successfully.")


if __name__ == "__main__":
    main()