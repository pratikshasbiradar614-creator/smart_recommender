import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Text fields carry the strongest semantic information for movie discovery.
TEXT_WEIGHTS = {
    "title": 1.0,
    "overview": 3.0,
    "genres_text": 4.0,
    "keywords_text": 2.5,
    "cast_text": 1.5,
    "director_text": 2.0,
    "original_language": 0.5,
}


def _safe_text(series):
    return series.fillna("").astype(str).str.strip()


def _prepare_text_features(df):
    """
    Build a weighted TF-IDF matrix from available movie text fields.
    Missing columns are safely treated as empty text.
    """
    parts = []

    for column, weight in TEXT_WEIGHTS.items():
        if column not in df.columns:
            continue

        values = _safe_text(df[column])

        # Repeat the field according to its weight so important fields
        # contribute more strongly to the vector.
        repeat_count = max(1, round(weight))
        field_text = values

        for _ in range(repeat_count):
            parts.append(field_text)

    if not parts:
        return None

    combined = parts[0].copy()
    for part in parts[1:]:
        combined = combined + " " + part

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=30000,
        ngram_range=(1, 2),
        min_df=1,
    )

    return vectorizer.fit_transform(combined)


def recommend_movies(df, selected_title, top_n=5):
    """
    Return recommended movies with:
      - similarity: score from 0 to 1
      - similarity_score: same score from 0 to 1

    The selected movie itself is excluded.
    """
    if df is None or df.empty or "title" not in df.columns:
        return pd.DataFrame()

    try:
        top_n = max(1, int(top_n))
    except (TypeError, ValueError):
        top_n = 5

    titles = _safe_text(df["title"])
    query = str(selected_title).strip().lower()

    exact_matches = np.where(titles.str.lower() == query)[0]

    if len(exact_matches) == 0:
        partial_matches = np.where(
            titles.str.lower().str.contains(query, regex=False, na=False)
        )[0]
        exact_matches = partial_matches

    if len(exact_matches) == 0:
        return pd.DataFrame()

    selected_index = int(exact_matches[0])
    matrix = _prepare_text_features(df)

    if matrix is None:
        return pd.DataFrame()

    scores = cosine_similarity(
        matrix[selected_index],
        matrix,
    ).ravel()

    ranked_indices = np.argsort(scores)[::-1]
    result_indices = [
        int(index)
        for index in ranked_indices
        if int(index) != selected_index
    ][:top_n]

    if not result_indices:
        return pd.DataFrame()

    results = df.iloc[result_indices].copy().reset_index(drop=True)

    result_scores = [
        round(float(np.clip(scores[index], 0.0, 1.0)), 4)
        for index in result_indices
    ]

    # Both names are retained for compatibility with the current app.
    results["similarity"] = result_scores
    results["similarity_score"] = result_scores

    return results
