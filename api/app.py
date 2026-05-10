import sqlite3
import logging
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    connection = sqlite3.connect("data/netflix.db")
    connection.row_factory = sqlite3.Row
    logger.info("Database connection established.")
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
        raise HTTPException(status_code=404, detail="Title not found")

    return dict(row)

    


@app.get("/stats", tags=["Statistics"])
def get_stats():
    """Return summary stats: total titles, count by type, and top 10 countries."""

    connection = get_db_connection()
    cursor = connection.cursor()

    total = cursor.execute("SELECT COUNT(*) FROM titles").fetchone()[0]

    type_rows = cursor.execute("SELECT type, COUNT(*) as count FROM titles GROUP BY type").fetchall()
    count_by_type = {row["type"]: row["count"] for row in type_rows}

    country_rows = cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM titles
        GROUP BY country
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    top_countries = [{"country": row["country"], "count": row["count"]} for row in country_rows]

    connection.close()

    return {
        "total_titles": total,
        "count_by_type": count_by_type,
        "top_10_countries": top_countries
    }


if __name__ == "__main__":
    
    uvicorn.run("app:app", host="0.0.0.0", port=8009, reload=True)
