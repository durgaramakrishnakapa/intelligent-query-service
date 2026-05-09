# NOTES

## 1. CSV Problems Found

While analyzing the Netflix dataset, I found several data quality issues that could affect both structured filtering and retrieval-based question answering.

### Missing values

Several important columns contained missing values:

- `director`: 1969 missing values
- `cast`: 570 missing values
- `country`: 476 missing values
- `date_added`: 11 missing values
- `rating`: 10 missing values

**Fix:** Missing values were replaced with meaningful placeholders — `Unknown Director`, `Cast Not Available`, `Country Not Available`, `Date Not Available`, `Rating Not Available`.

**Why:** This prevents null-related failures during filtering, chunk creation, and embedding generation.

### Inconsistent categorical values

Categorical columns had inconsistent formatting. Examples: `tv show`, `Tv Show`, `TV Show`. This creates filtering problems because logically identical values are treated differently.

**Fix:** Standardized all TV show variations to `TV Show` and movie variations to `Movie`. Ratings were also converted to uppercase.

### Irregular spacing in text columns

Some text columns contained leading/trailing whitespace across: title, director, cast, country, rating, listed_in, description, type.

**Fix:** Applied whitespace trimming to all affected columns.

### Inconsistent formatting in multi-value columns

Columns like `country`, `cast`, and `listed_in` contained inconsistent comma spacing (e.g. `India,United States`, `India , United States`).

**Fix:** Normalized all comma-separated values to consistent `value, value` format using regex.

### What was left unchanged

- **Country normalization:** Some rows contain multiple countries (e.g. `United States, India`). These were intentionally not split into normalized relational tables. The assignment required a lightweight implementation and substring filtering with `LIKE` was sufficient.
- **Date parsing:** `date_added` was not converted to datetime format. The current APIs and RAG pipeline do not require date-based filtering, so keeping it as text reduced unnecessary preprocessing complexity.

---

## 2. Schema Decisions

Multi-value fields such as `country`, `cast`, and `listed_in` were stored as plain text comma-separated strings in the SQLite `titles` table instead of creating separate normalized relational tables.

Examples:
- `country` → `United States, India`
- `cast` → `Actor 1, Actor 2, Actor 3`
- `listed_in` → `Comedies, Romantic Movies`

**1. Simplicity** — The assignment required a lightweight implementation. Creating separate tables like `title_countries`, `title_cast`, `title_genres` with foreign keys and joins would increase complexity significantly.

**2. Structured filtering still works** — For API filtering, substring matching was sufficient:
```sql
WHERE country LIKE '%India%'
```

**3. Better for RAG** — The RAG pipeline converts each row into a single text chunk for embeddings. Keeping these values together improves semantic context for retrieval:
```
Country: United States, India
Cast: Actor 1, Actor 2
Genres: Comedies, Romantic Movies
```

---

## 3. RAG Choices

Instead of traditional single-index retrieval, a sharded parallel retrieval architecture was implemented.

**Pipeline:**
- Each title row converted into one structured chunk
- 6234 rows → 6234 chunks
- Chunks split into 20 FAISS shards
- User query embedded with `all-MiniLM-L6-v2`
- Parallel search across all shards
- Top 3 retrieved from each shard
- Global similarity reranking
- Top 6 chunks passed to Gemini 2.5 Flash

**Why:** This improves retrieval scalability and reduces search latency while maintaining grounded answers.

---

## 4. What Would Break at 100,000 Titles

- **RAG retrieval cost increases** — More titles means more chunks, larger FAISS indexes, and higher memory usage and search time.
- **20-shard design may become inefficient** — Each shard would become much larger, increasing retrieval latency. More balanced sharding or distributed vector storage would be needed.
- **Embedding/index build time becomes heavy** — Creating embeddings for 100k titles would take much longer during preprocessing.
- **Gemini context quality risk** — With a much larger dataset, retrieval precision becomes more important; weak retrieval could send less relevant chunks to the LLM.

**Better production solution:** A scalable vector database instead of local FAISS shards, and stronger reranking for better retrieval accuracy.

---

## 5. AI Usage

I used AI tools significantly during development, mainly ChatGPT, but I made architectural decisions myself and reviewed code before using it.

For the dataset cleaning phase, I gave the CSV structure to ChatGPT and asked for suggested cleaning improvements. It suggested handling missing values, trimming whitespace, standardizing categorical values, validating data types, and duplicate checking — all of which I implemented after reviewing them.

ChatGPT also suggested a more normalized database design with separate tables for countries, cast members, and genres. I intentionally rejected that because the assignment's filtering requirements (country, release_year, type, rating) are simple enough to support from a single table, and SQL `LIKE` queries were sufficient for multi-value fields at this scale.

I also used ChatGPT to help generate some implementation code (cleaning functions, database connection structure), but reviewed and adjusted the code before using it.

For testing, I used Kiro IDE to generate test cases by scanning the project files. Testing is an area I am still new to — in my previous beginner-level projects I had not worked much with formal test writing. I accepted more help there than in other areas, though I still reviewed the generated tests.

For the RAG system, the overall architecture was my own decision — FAISS, all-MiniLM-L6-v2, Gemini 2.5 Flash, sharded retrieval, parallel search, and similarity reranking. The shard-based parallel retrieval idea came from patterns I had seen in a previous project, not from AI suggestions.

One area where I initially relied on AI without full understanding was Python SQLite cursor usage (`cursor.execute()` and query execution from Python). I was new to that pattern at first, but understood it after implementing and debugging it.

Overall, I used AI as a development assistant, not as an unreviewed code generator. Where I disagreed with suggestions, I changed the design based on project requirements.

---

## 6. What Would I Do With Another 4 Hours

- **Smarter shard routing instead of generic sharding**  
  Currently, shard splitting is generic. With more time, I would implement domain-based sharding, such as separating Movies and TV Shows (and potentially by genre or country). Then, based on the user query, the system could intelligently route retrieval only to relevant shards instead of searching all shards. This would reduce latency and improve retrieval accuracy.
- **Build a frontend UI** — A simple frontend for both the structured filtering system and the RAG question-answering system, so the project becomes easier to interact with instead of using only API endpoints.
- **Add caching for RAG performance** — Cache frequently used resources such as the embedding model, FAISS indexes, and repeated query results to reduce response time.
- 
