"""Tests for POST /ask endpoint and RAG service."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from rag.ask_api import app


@pytest.fixture
def client():
    """Return a FastAPI test client for the RAG app."""
    return TestClient(app)


@pytest.fixture
def mock_chunks():
    """Sample retrieved chunks to simulate retriever output."""
    return [
        {"show_id": "s1", "title": "Dangal", "text": "Show ID: s1\nTitle: Dangal\nType: Movie\nCountry: India\nDescription: A wrestling story.", "score": 0.95},
        {"show_id": "s2", "title": "Sacred Games", "text": "Show ID: s2\nTitle: Sacred Games\nType: TV Show\nCountry: India\nDescription: A crime saga.", "score": 0.88},
    ]


def test_ask_returns_answer_and_show_ids(client, mock_chunks):
    """/ask should return both answer and show_ids in the response."""
    mock_result = {"answer": "Dangal is a great movie.", "sources": ["s1"]}

    with patch("rag.ask_api.ask_gemini", return_value=mock_result):
        response = client.post("/ask", json={"question": "Suggest a sports movie from India"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "show_ids" in data


def test_ask_show_ids_not_empty_when_answer_exists(client, mock_chunks):
    """/ask should return at least one show_id when answer is non-empty."""
    mock_result = {"answer": "Dangal is a great movie.", "sources": ["s1", "s2"]}

    with patch("rag.ask_api.ask_gemini", return_value=mock_result):
        response = client.post("/ask", json={"question": "Suggest a sports movie from India"})

    data = response.json()
    if data["answer"]:
        assert len(data["show_ids"]) > 0


def test_ask_requires_question_field(client):
    """/ask should return 422 if question field is missing."""
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_build_context_joins_chunks():
    """build_context should join chunk texts with double newline."""
    from rag.rag_service import build_context
    chunks = [
        {"text": "Title: Dangal"},
        {"text": "Title: Sacred Games"},
    ]
    context = build_context(chunks)
    assert "Title: Dangal" in context
    assert "Title: Sacred Games" in context
    assert "\n\n" in context


def test_build_prompt_contains_query_and_context():
    """build_prompt should include both the query and context in the output."""
    from rag.rag_service import build_prompt
    prompt = build_prompt("best Indian movies", "Title: Dangal")
    assert "best Indian movies" in prompt
    assert "Title: Dangal" in prompt
