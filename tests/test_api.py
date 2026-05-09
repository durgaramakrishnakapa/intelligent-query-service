"""Tests for api/app.py endpoints."""

import sqlite3
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.app import app


@pytest.fixture
def client():
    """Return a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_db(tmp_path):
    """Create a temporary SQLite DB with sample titles for testing."""
    db_path = str(tmp_path / "test.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE titles (
            show_id TEXT PRIMARY KEY,
            type TEXT,
            title TEXT,
            director TEXT,
            cast TEXT,
            country TEXT,
            date_added TEXT,
            release_year INTEGER,
            rating TEXT,
            duration TEXT,
            listed_in TEXT,
            description TEXT
        )
    """)

    cursor.executemany("INSERT INTO titles VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", [
        ("s1", "Movie", "Dangal", "Nitesh", "Aamir Khan", "India", "Jan 1, 2017", 2016, "TV-PG", "161 min", "Dramas", "A wrestling story."),
        ("s2", "TV Show", "Sacred Games", "Vikram", "Nawazuddin", "India", "Jul 6, 2018", 2018, "TV-MA", "2 Seasons", "Crime", "A crime saga."),
        ("s3", "Movie", "Inception", "Nolan", "DiCaprio", "United States", "Jan 1, 2015", 2010, "PG-13", "148 min", "Sci-Fi", "A dream heist."),
    ])

    connection.commit()
    connection.close()
    return db_path


def make_connection(db_path):
    """Create a new thread-safe SQLite connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_get_titles_returns_paginated_response(client, mock_db):
    """GET /titles should return page, page_size, total, and results."""
    with patch("api.app.get_db_connection", side_effect=lambda: make_connection(mock_db)):
        response = client.get("/titles?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "total" in data
    assert "results" in data


def test_get_titles_filter_by_country(client, mock_db):
    """GET /titles?country=India should return only Indian titles."""
    with patch("api.app.get_db_connection", side_effect=lambda: make_connection(mock_db)):
        response = client.get("/titles?country=India")

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) > 0
    for title in results:
        assert "India" in title["country"]


def test_get_title_by_id_returns_correct_title(client, mock_db):
    """GET /titles/{show_id} should return the correct title."""
    with patch("api.app.get_db_connection", side_effect=lambda: make_connection(mock_db)):
        response = client.get("/titles/s1")

    assert response.status_code == 200
    assert response.json()["show_id"] == "s1"
    assert response.json()["title"] == "Dangal"


def test_get_title_by_id_returns_404_for_missing(client, mock_db):
    """GET /titles/{show_id} should return 404 for a non-existent show_id."""
    with patch("api.app.get_db_connection", side_effect=lambda: make_connection(mock_db)):
        response = client.get("/titles/nonexistent_id")

    assert response.status_code == 404


def test_get_stats_returns_required_keys(client, mock_db):
    """GET /stats should return total_titles, count_by_type, and top_10_countries."""
    with patch("api.app.get_db_connection", side_effect=lambda: make_connection(mock_db)):
        response = client.get("/stats")

    assert response.status_code == 200
    data = response.json()
    assert "total_titles" in data
    assert "count_by_type" in data
    assert "top_10_countries" in data
