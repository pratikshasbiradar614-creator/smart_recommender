import numpy as np


def dot_similarity(a, b):
    """
    Calculate dot product similarity.
    """
    return float(np.dot(a, b))


def cosine_similarity(a, b):
    """
    Calculate cosine similarity between two vectors.
    """

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)