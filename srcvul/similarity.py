# srcvul/similarity.py

from dataclasses import dataclass
from typing import List

import numpy as np

from .vectors import VSVect


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two 1D numpy arrays.
    Returns a value in [-1, 1]. For our vsvectors we expect [0, 1].
    """
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


@dataclass
class Match:
    """
    Represents a match between a target vsvector and a DB vsvector.
    """
    target: VSVect
    db: VSVect
    similarity: float


def find_matches(
    target_vectors: List[VSVect],
    db_vectors: List[VSVect],
    threshold: float = 0.8,
) -> List[Match]:
    """
    Brute-force search: compare each target vsvector with each DB vsvector,
    keep those with cosine similarity >= threshold.
    This is fine for a small ICPC demo DB.
    """
    matches: List[Match] = []
    for t in target_vectors:
        t_arr = t.as_array()
        for d in db_vectors:
            d_arr = d.as_array()
            sim = cosine_similarity(t_arr, d_arr)
            if sim >= threshold:
                matches.append(Match(target=t, db=d, similarity=sim))
    return matches
