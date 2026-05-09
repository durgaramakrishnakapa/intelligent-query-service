"""Load, clean, and store Netflix dataset into SQLite."""

import sqlite3
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    df["type"] = df["type"].replace({
        "tv show": "TV Show",
        "Tv Show": "TV Show",
        "TV Show": "TV Show",
        "movie": "Movie",
        "Movie": "Movie"
    })

    df["rating"] = df["rating"].str.upper()

    return df


def normalize_multi_value_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize spacing in comma-separated columns."""

    multi_value_columns = ["country", "cast", "listed_in"]

    for column in multi_value_columns:
        df[column] = df[column].str.replace(r"\s*,\s*", ", ", regex=True)

    return df

def validate_release_year(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure release_year is stored as an integer."""

    df["release_year"] = df["release_year"].astype(int)

    return df


def remove_duplicate_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove exact duplicate rows from the dataset."""

    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()

    return df, duplicate_count


def create_database_connection(db_path: str) -> sqlite3.Connection:
    """Create and return a SQLite database connection."""

    connection = sqlite3.connect(db_path)
    return connection


def create_titles_table(connection: sqlite3.Connection) -> None:
    """Create the titles table in the SQLite database."""

    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS titles")

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

    connection.commit()


def insert_cleaned_data(connection: sqlite3.Connection, df: pd.DataFrame) -> None:
    """Insert cleaned records into the database."""

    df.to_sql("titles", connection, if_exists="append", index=False)

def print_summary_report(
    total_rows: int,
    final_rows: int,
    missing_report: dict,
    duplicates_removed: int
) -> None:
    """Print a summary of the ingestion process."""

    print("\nINGESTION SUMMARY")
    print("-" * 40)
    print(f"Total rows loaded: {total_rows}")
    print(f"Final rows inserted: {final_rows}")
    print(f"Duplicates removed: {duplicates_removed}")

    print("\nMissing values fixed:")
    for column, count in missing_report.items():
        print(f"{column}: {count}")

def main() -> None:
    """Run the complete data ingestion pipeline."""

    csv_path = "data/netflix_titles.csv"

    df = load_csv_data(csv_path)

    logger.info("CSV loaded successfully.")
    logger.info(df.head().to_string())

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

    logger.info("Text cleaning completed.")
    logger.info(df.head().to_string())

    df, missing_report = handle_missing_values(df)

    logger.info("Missing values handled successfully.")
    logger.info(df.isnull().sum().to_string())
    logger.info(missing_report)

    df = standardize_columns(df)

    logger.info("Column standardization completed.")
    logger.info(df[["type", "rating"]].head().to_string())

    df = normalize_multi_value_columns(df)

    logger.info("Multi-value column normalization completed.")
    logger.info(df[["country", "cast", "listed_in"]].head().to_string())

    df = validate_release_year(df)

    logger.info("Release year validation completed.")
    logger.info(df["release_year"].dtype)

    df, duplicate_count = remove_duplicate_rows(df)

    logger.info("Duplicate removal completed.")
    logger.info(f"Duplicates removed: {duplicate_count}")

    db_path = "data/netflix.db"

    connection = create_database_connection(db_path)

    logger.info("Database connection created successfully.")

    create_titles_table(connection)

    logger.info("Titles table created successfully.")

    insert_cleaned_data(connection, df)

    logger.info("Cleaned data inserted successfully.")

    print_summary_report(
    total_rows=len(load_csv_data(csv_path)),
    final_rows=len(df),
    missing_report=missing_report,
    duplicates_removed=duplicate_count
    )

    connection.close()

    logger.info("Database connection closed.")

if __name__ == "__main__":
    main()

