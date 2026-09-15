"""
CineVerse recommendation explanations.

This module safely compares text and numeric movie fields.
It never converts movie overviews or other text fields to float.
"""

import re
import pandas as pd


IGNORED_FEATURES = {
    "title",
    "overview",
    "description",
    "movie_id",
    "id",
    "similarity",
    "similarity_score",
    "combined_features",
}


def _is_missing(value):
    try:
        result = pd.isna(value)
        return bool(result)
    except (TypeError, ValueError):
        return value is None


def _clean_value(value):
    if _is_missing(value):
        return ""
    return str(value).strip()


def _format_feature_name(feature):
    name = (
        str(feature)
        .replace("_text", "")
        .replace("_", " ")
        .replace("-", " ")
        .strip()
    )
    return name.title()


def _tokens(value):
    """
    Split categorical text safely.
    Supports values such as:
    Action|Adventure, Comedy, ['Action', 'Adventure']
    """
    text = _clean_value(value).lower()
    if not text:
        return set()

    text = text.replace("[", "").replace("]", "")
    text = text.replace("'", "").replace('"', "")
    parts = re.split(r"[|,;/]+", text)

    return {part.strip() for part in parts if part.strip()}


def _numeric(value):
    try:
        if _is_missing(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def get_shared_features(selected_row, recommended_row, feature_columns):
    """
    Return meaningful shared characteristics between two movies.
    Text columns are compared as tokens; numeric columns are compared
    only when they are genuinely numeric.
    """
    shared = []

    # Prefer meaningful movie attributes in this order.
    preferred_order = [
        "genres_text",
        "keywords_text",
        "cast_text",
        "director_text",
        "original_language",
        "release_year",
        "vote_average",
        "cast_count",
        "runtime",
    ]

    available = [f for f in preferred_order if f in feature_columns]
    available += [
        f for f in feature_columns
        if f not in available
    ]

    for feature in available:
        feature_key = str(feature).lower()

        if feature_key in IGNORED_FEATURES:
            continue
        if feature not in selected_row.index or feature not in recommended_row.index:
            continue

        selected_value = selected_row[feature]
        recommended_value = recommended_row[feature]

        if _is_missing(selected_value) or _is_missing(recommended_value):
            continue

        selected_text = _clean_value(selected_value)
        recommended_text = _clean_value(recommended_value)

        if not selected_text or not recommended_text:
            continue

        selected_number = _numeric(selected_value)
        recommended_number = _numeric(recommended_value)

        # Numeric comparison: only label it shared when close.
        if selected_number is not None and recommended_number is not None:
            difference = abs(selected_number - recommended_number)
            tolerance = max(abs(selected_number), abs(recommended_number), 1.0) * 0.12

            if difference <= tolerance:
                shared.append(_format_feature_name(feature))
            continue

        # Text/categorical comparison.
        selected_tokens = _tokens(selected_value)
        recommended_tokens = _tokens(recommended_value)

        if selected_tokens and recommended_tokens:
            if selected_tokens.intersection(recommended_tokens):
                shared.append(_format_feature_name(feature))

    # Remove duplicates and keep only useful labels.
    return list(dict.fromkeys(shared))[:6]


def _fallback_explanation(
    selected_title,
    recommended_title,
    similarity_score,
    shared_features,
):
    if shared_features:
        feature_text = ", ".join(shared_features)
        return (
            f"{recommended_title} is a good match for {selected_title} "
            f"because both movies share {feature_text.lower()}. "
            f"The calculated similarity is {similarity_score:.1f}%."
        )

    return (
        f"{recommended_title} was selected because its available movie "
        f"features are similar to {selected_title}. "
        f"The calculated similarity is {similarity_score:.1f}%."
    )


def explain_recommendation(
    selected_title,
    recommended_title,
    similarity_score,
    selected_row,
    recommended_row,
    feature_columns,
):
    shared_features = get_shared_features(
        selected_row,
        recommended_row,
        feature_columns,
    )

    fallback = _fallback_explanation(
        selected_title,
        recommended_title,
        similarity_score,
        shared_features,
    )

    # Ollama is optional. The app remains functional without it.
    try:
        import requests

        prompt = f"""
You are CineBuddy, the explanation assistant inside CineVerse.

Selected movie: {selected_title}
Recommended movie: {recommended_title}
Similarity score: {similarity_score:.1f}%
Shared characteristics: {", ".join(shared_features) if shared_features else "No specific shared characteristic identified"}

Write exactly 2 short, natural sentences.
Use only the information provided.
Do not invent plot details, actors, ratings, dates, genres, or awards.
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False,
            },
            timeout=15,
        )

        if response.ok:
            generated = response.json().get("response", "").strip()
            if generated:
                return {
                    "shared_features": shared_features,
                    "explanation": generated,
                }

    except Exception:
        pass

    return {
        "shared_features": shared_features,
        "explanation": fallback,
    }
