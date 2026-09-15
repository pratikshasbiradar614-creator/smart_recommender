import pandas as pd


def load_movies(file_path="movies.csv"):
    """
    Load movie data from CSV.
    """
    return pd.read_csv(file_path)


def get_feature_columns(df):
    """
    Return numerical feature columns.
    """
    return [
        column
        for column in df.columns
        if column != "title"
    ]