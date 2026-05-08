import sqlite3
from fastapi import FastAPI, Query
from typing import Optional

def get_db_connection():
    connection = sqlite3.connect("data/netflix.db")
    connection.row_factory = sqlite3.Row
    print("Database connection established.")
    return connection

app = FastAPI()

@app.get("/titles", tags=["Title Listing"])
def get_titles(
    country: Optional[str] = Query(default=None),
    release_year: Optional[int] = Query(default=None),
    type: Optional[str] = Query(default=None),
    rating: Optional[str] = Query(default=None),
    page: int = Query(default=1),
    page_size: int = Query(default=10)
):
    """List titles with optional filters for country, release_year, type, and rating. Supports pagination."""

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM titles WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM titles WHERE 1=1"
    params = []

    if country:
        query += " AND country LIKE ?"
        count_query += " AND country LIKE ?"
        params.append(f"%{country}%")

    if release_year:
        query += " AND release_year = ?"
        count_query += " AND release_year = ?"
        params.append(release_year)

    if type:
        query += " AND type = ?"
        count_query += " AND type = ?"
        params.append(type)

    if rating:
        query += " AND rating = ?"
        count_query += " AND rating = ?"
        params.append(rating)

    total = cursor.execute(count_query, params).fetchone()[0]

    offset = (page - 1) * page_size
    query += " LIMIT ? OFFSET ?"
    params.append(page_size)
    params.append(offset)

    rows = cursor.execute(query, params).fetchall()
    connection.close()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": [dict(row) for row in rows]
    }


@app.get("/titles/{show_id}", tags=["Title Details"])
def get_title_by_id(show_id: str):
    """Fetch a single title by its show_id."""

    connection = get_db_connection()
    cursor = connection.cursor()

    row = cursor.execute("SELECT * FROM titles WHERE show_id = ?", (show_id,)).fetchone()
    connection.close()

    if row is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Title not found")

    return dict(row)

    


@app.get("/stats", tags=["Statistics"])
def get_stats():
    """Return summary stats: total titles, count by type, and top 10 countries."""
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8009, reload=True)
