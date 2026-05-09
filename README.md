# intelligent-query-service
---

## Setup

```bash
# Clone the repo and create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create a .env file in the project root with your Gemini API key
# .env
GEMINI_API_KEY=your_api_key_here
```

---

## How to run

**Step 1 — Ingest the dataset**

```bash
python ingest.py
```

**Step 2 — Build RAG embeddings** (required before using `/ask`)

```bash
python rag/chunk_builder.py
python rag/embed_and_index.py
```

**Step 3 — Start the main API** (titles, stats)

```bash
python api/app.py
```

API runs at: `http://localhost:8009`

**Step 4 — Start the RAG API** (ask endpoint)

```bash
uvicorn rag.ask_api:app --port 8010
```

API runs at: `http://localhost:8010`

---

## How to test

```bash
pytest tests/ -v
```

---

## Known limitations

- The main API (`api/app.py`) and the RAG `/ask` endpoint (`rag/ask_api.py`) are two separate FastAPI apps. They run on different ports and are not combined into one.
- Embeddings must be built manually by running `chunk_builder.py` and `embed_and_index.py` before the `/ask` endpoint will work. Skipping this step will cause the RAG pipeline to fail.
