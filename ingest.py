"""Load, clean, and store Netflix dataset into SQLite."""

import sqlite3
import pandas as pd


def load_csv_data(csv_path: str) -> pd.DataFrame:
    """Load Netflix CSV data into a pandas DataFrame."""
    df = pd.read_csv(csv_path)
    return df


def clean_text_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Remove extra spaces from text columns."""
    
    for column in columns:
        df[column] = df[column].str.strip()
    
    return df


def handle_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Replace missing values with default placeholders."""

    missing_report = {
        "director": df["director"].isnull().sum(),
        "cast": df["cast"].isnull().sum(),
        "country": df["country"].isnull().sum(),
        "date_added": df["date_added"].isnull().sum(),
        "rating": df["rating"].isnull().sum()
    }

    df["director"] = df["director"].fillna("Unknown Director")
    df["cast"] = df["cast"].fillna("Cast Not Available")
    df["country"] = df["country"].fillna("Country Not Available")
    df["date_added"] = df["date_added"].fillna("Date Not Available")
    df["rating"] = df["rating"].fillna("Rating Not Available")

    return df, missing_report


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize categorical column formatting."""


def normalize_multi_value_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize spacing in comma-separated columns."""


def validate_release_year(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure release_year is stored as an integer."""


def remove_duplicate_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove exact duplicate rows from the dataset."""


def create_database_connection(db_path: str) -> sqlite3.Connection:
    """Create and return a SQLite database connection."""


def create_titles_table(connection: sqlite3.Connection) -> None:
    """Create the titles table in the SQLite database."""


def insert_cleaned_data(connection: sqlite3.Connection, df: pd.DataFrame) -> None:
    """Insert cleaned records into the database."""


def print_summary_report(
    total_rows: int,
    final_rows: int,
    missing_report: dict,
    duplicates_removed: int
) -> None:
    """Print a summary of the ingestion process."""


def main() -> None:
    """Run the complete data ingestion pipeline."""

    csv_path = "data/netflix_titles.csv"

    df = load_csv_data(csv_path)

    print("CSV loaded successfully.")
    print(df.head())

    text_columns = [
        "title",
        "director",
        "cast",
        "country",
        "rating",
        "listed_in",
        "description",
        "type"
    ]

    df = clean_text_columns(df, text_columns)

    print("\nText cleaning completed.")
    print(df.head())


    df, missing_report = handle_missing_values(df)

    print("\nMissing values handled successfully.")
    print(df.isnull().sum())
    print(missing_report)

if __name__ == "__main__":
    main()

