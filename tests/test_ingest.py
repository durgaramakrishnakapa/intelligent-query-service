"""Tests for ingest.py data pipeline functions."""

import pandas as pd
import pytest
from ingest import (
    clean_text_columns,
    handle_missing_values,
    remove_duplicate_rows,
    standardize_columns,
    validate_release_year,
)


@pytest.fixture
def sample_df():
    """Minimal DataFrame that mimics the Netflix CSV structure."""
    return pd.DataFrame({
        "show_id": ["s1", "s2", "s3"],
        "type": ["Movie", "TV Show", "movie"],
        "title": ["  Inception  ", "Breaking Bad", "Parasite"],
        "director": ["Nolan", None, "Bong"],
        "cast": ["DiCaprio", None, "Song"],
        "country": ["United States", None, "South Korea"],
        "date_added": ["Jan 1, 2020", None, "Feb 2, 2021"],
        "rating": ["pg-13", "tv-ma", "r"],
        "release_year": [2010, 2008, 2019],
        "duration": ["148 min", "5 Seasons", "132 min"],
        "listed_in": ["Sci-Fi", "Drama", "Thriller"],
        "description": ["A dream heist.", "A chemistry teacher.", "A poor family."],
    })


def test_clean_text_columns_strips_whitespace(sample_df):
    """clean_text_columns should strip leading and trailing spaces."""
    df = clean_text_columns(sample_df, ["title"])
    assert df["title"].iloc[0] == "Inception"


def test_handle_missing_values_fills_placeholders(sample_df):
    """handle_missing_values should replace NaN with placeholder strings."""
    df, _ = handle_missing_values(sample_df)
    assert df["director"].iloc[1] == "Unknown Director"
    assert df["cast"].iloc[1] == "Cast Not Available"
    assert df["country"].iloc[1] == "Country Not Available"


def test_remove_duplicate_rows_drops_exact_duplicates(sample_df):
    """remove_duplicate_rows should remove exact duplicate rows."""
    df_with_dupes = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
    df_clean, count = remove_duplicate_rows(df_with_dupes)
    assert count == 1
    assert len(df_clean) == len(sample_df)


def test_standardize_columns_normalizes_type(sample_df):
    """standardize_columns should normalize type values to Movie or TV Show."""
    df = standardize_columns(sample_df)
    assert set(df["type"].unique()).issubset({"Movie", "TV Show"})


def test_validate_release_year_returns_int(sample_df):
    """validate_release_year should ensure release_year column is integer dtype."""
    df = validate_release_year(sample_df)
    assert df["release_year"].dtype == int
