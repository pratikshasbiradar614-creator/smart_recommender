import ast
import json
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, "tmdb_5000_movies.csv")
CREDITS_FILE = os.path.join(BASE_DIR, "tmdb_5000_credits.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "movies.csv")


def parse_json_names(value, key="name", limit=None):
    if pd.isna(value):
        return ""

    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        try:
            data = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return ""

    if not isinstance(data, list):
        return ""

    names = []
    for item in data:
        if isinstance(item, dict) and item.get(key):
            names.append(str(item[key]))

    return " ".join(names[:limit] if limit else names)


def parse_director(value):
    if pd.isna(value):
        return ""

    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        try:
            data = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return ""

    if not isinstance(data, list):
        return ""

    for item in data:
        if (
            isinstance(item, dict)
            and item.get("job") == "Director"
            and item.get("name")
        ):
            return str(item["name"])

    return ""


def main():
    if not os.path.exists(MOVIES_FILE):
        raise FileNotFoundError(
            "tmdb_5000_movies.csv is missing from the project folder."
        )

    if not os.path.exists(CREDITS_FILE):
        raise FileNotFoundError(
            "tmdb_5000_credits.csv is missing from the project folder."
        )

    movies = pd.read_csv(MOVIES_FILE)
    credits = pd.read_csv(CREDITS_FILE)

    credits = credits.rename(columns={"movie_id": "id"})
    credits = credits[["id", "cast", "crew"]]

    df = movies.merge(credits, on="id", how="left")

    df["genres_text"] = df["genres"].apply(parse_json_names)
    df["keywords_text"] = df["keywords"].apply(parse_json_names)
    df["cast_text"] = df["cast"].apply(
        lambda value: parse_json_names(value, limit=8)
    )
    df["director_text"] = df["crew"].apply(parse_director)

    for column in ["title", "overview", "original_language", "release_date"]:
        if column not in df.columns:
            df[column] = ""
        df[column] = df[column].fillna("").astype(str)

    df["overview"] = df["overview"].replace("nan", "")

    df["release_year"] = (
        pd.to_datetime(df["release_date"], errors="coerce")
        .dt.year.fillna(0)
        .astype(int)
    )

    numeric_defaults = {
        "budget": 0,
        "popularity": 0,
        "vote_average": 0,
        "vote_count": 0,
        "runtime": 0,
    }

    for column, default in numeric_defaults.items():
        if column not in df.columns:
            df[column] = default
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        ).fillna(default)

    df["genre_count"] = df["genres_text"].str.split().apply(
        lambda values: len(values) if values != [""] else 0
    )
    df["cast_count"] = df["cast_text"].str.split().apply(
        lambda values: len(values) if values != [""] else 0
    )
    df["keyword_count"] = df["keywords_text"].str.split().apply(
        lambda values: len(values) if values != [""] else 0
    )

    output_columns = [
        "title",
        "overview",
        "genres_text",
        "keywords_text",
        "cast_text",
        "director_text",
        "original_language",
        "release_date",
        "release_year",
        "budget",
        "popularity",
        "vote_average",
        "vote_count",
        "runtime",
        "genre_count",
        "cast_count",
        "keyword_count",
    ]

    df = df[output_columns].copy()
    df = df[df["title"].str.strip().ne("")]
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("=" * 50)
    print("CineVerse dataset preparation completed!")
    print(f"Movies available: {len(df)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()
