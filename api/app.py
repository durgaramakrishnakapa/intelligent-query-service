import sqlite3
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()


@app.get("/titles")
def get_titles():
    """List titles with optional filters for country, release_year, type, and rating. Supports pagination."""
    pass


@app.get("/titles/{show_id}")
def get_title_by_id(show_id: str):
    """Fetch a single title by its show_id."""
    pass


@app.get("/stats")
def get_stats():
    """Return summary stats: total titles, count by type, and top 10 countries."""
    pass

