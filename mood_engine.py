import pandas as pd
import numpy as np


MOOD_PROFILES = {
    "😌 Chill & Feel-Good": {
        "keywords": [
            "comedy",
            "feel good",
            "family",
            "friendship",
            "animation",
            "music",
            "adventure"
        ],
        "preferred_genres": [
            "comedy",
            "animation",
            "family",
            "musical",
            "adventure"
        ]
    },

    "😂 Make Me Laugh": {
        "keywords": [
            "comedy",
            "funny",
            "humor",
            "satire",
            "parody"
        ],
        "preferred_genres": [
            "comedy"
        ]
    },

    "😭 Emotional Ride": {
        "keywords": [
            "drama",
            "emotional",
            "love",
            "loss",
            "family",
            "life",
            "romance"
        ],
        "preferred_genres": [
            "drama",
            "romance",
            "family"
        ]
    },

    "🔥 Action & Adventure": {
        "keywords": [
            "action",
            "adventure",
            "fight",
            "war",
            "hero",
            "mission",
            "superhero"
        ],
        "preferred_genres": [
            "action",
            "adventure",
            "thriller"
        ]
    },

    "🧠 Mind-Blowing": {
        "keywords": [
            "mystery",
            "psychological",
            "mind",
            "science fiction",
            "sci-fi",
            "twist",
            "time",
            "space",
            "crime"
        ],
        "preferred_genres": [
            "mystery",
            "thriller",
            "science fiction",
            "sci-fi",
            "crime"
        ]
    },

    "👻 Spooky Night": {
        "keywords": [
            "horror",
            "ghost",
            "haunted",
            "supernatural",
            "monster",
            "dark",
            "zombie",
            "vampire"
        ],
        "preferred_genres": [
            "horror",
            "thriller",
            "mystery"
        ]
    },

    "💖 Romance": {
        "keywords": [
            "romance",
            "love",
            "relationship",
            "couple",
            "marriage",
            "heart"
        ],
        "preferred_genres": [
            "romance",
            "drama"
        ]
    },

    "👨‍👩‍👧 Family Time": {
        "keywords": [
            "family",
            "children",
            "friendship",
            "animation",
            "comedy",
            "adventure"
        ],
        "preferred_genres": [
            "family",
            "animation",
            "comedy",
            "adventure"
        ]
    },

    "🚀 Sci-Fi Escape": {
        "keywords": [
            "space",
            "future",
            "robot",
            "science",
            "technology",
            "alien",
            "time travel",
            "sci-fi"
        ],
        "preferred_genres": [
            "science fiction",
            "sci-fi",
            "adventure"
        ]
    }
}


def _safe_text(value):
    """
    Converts any value into lowercase searchable text.
    """
    if pd.isna(value):
        return ""

    return str(value).lower()


def _get_movie_text(movie):
    """
    Combines useful movie columns into one searchable text.
    Works even if some columns are missing.
    """
    possible_columns = [
        "title",
        "genres",
        "genre",
        "overview",
        "description",
        "plot",
        "keywords",
        "tags",
        "cast",
        "director"
    ]

    text_parts = []

    for column in possible_columns:
        if column in movie.index:
            text_parts.append(_safe_text(movie[column]))

    return " ".join(text_parts)


def _get_genre_text(movie):
    """
    Returns genre-related text from a movie row.
    """
    genre_columns = ["genres", "genre", "tags"]

    genre_parts = []

    for column in genre_columns:
        if column in movie.index:
            genre_parts.append(_safe_text(movie[column]))

    return " ".join(genre_parts)


def calculate_mood_score(movie, mood_name):
    """
    Calculates how strongly a movie matches a selected mood.
    Returns a score between 0 and 100.
    """

    if mood_name not in MOOD_PROFILES:
        return 0.0

    profile = MOOD_PROFILES[mood_name]

    movie_text = _get_movie_text(movie)
    genre_text = _get_genre_text(movie)

    score = 0.0

    # Keyword matching
    for keyword in profile["keywords"]:
        if keyword in movie_text:
            score += 8

    # Genre matching gets higher weight
    for genre in profile["preferred_genres"]:
        if genre in genre_text:
            score += 15

    # Normalize score to maximum 100
    score = min(score, 100)

    return round(score, 2)


def recommend_by_mood(movies, mood_name, top_n=8):
    """
    Recommends movies based on the selected mood.
    """

    if movies is None or len(movies) == 0:
        return pd.DataFrame()

    results = movies.copy()

    results["mood_score"] = results.apply(
        lambda movie: calculate_mood_score(movie, mood_name),
        axis=1
    )

    # Sort by mood score
    results = results.sort_values(
        by="mood_score",
        ascending=False
    )

    # Keep only movies with a meaningful score
    matched_results = results[results["mood_score"] > 0]

    # If no movie matches, return top rows rather than blank screen
    if matched_results.empty:
        return results.head(top_n)

    return matched_results.head(top_n)


def get_mood_description(mood_name):
    """
    Small description shown in the UI.
    """

    descriptions = {
        "😌 Chill & Feel-Good":
            "Light, warm and comforting movies for a relaxed evening.",

        "😂 Make Me Laugh":
            "Funny, chaotic and entertaining movies to improve your mood.",

        "😭 Emotional Ride":
            "Stories that touch your heart and stay with you.",

        "🔥 Action & Adventure":
            "High-energy stories packed with missions, fights and excitement.",

        "🧠 Mind-Blowing":
            "Movies full of twists, mysteries and ideas that make you think.",

        "👻 Spooky Night":
            "Dark, mysterious and supernatural stories for a scary night.",

        "💖 Romance":
            "Love stories, relationships and emotional connections.",

        "👨‍👩‍👧 Family Time":
            "Fun and safe entertainment for friends and family.",

        "🚀 Sci-Fi Escape":
            "Travel through space, technology, future worlds and imagination."
    }

    return descriptions.get(
        mood_name,
        "Discover movies based on your current vibe."
    )