"""Algorithms and API calls for getting the similarity and contradiction between
the articles.
"""


# As float percentages.
THRES_SIMILARITY = 0.5
THRES_CONTRADICTION = 0.5


def _get_similarity_score(main, candidate):
    main_kw, candidate_kw = set(main.keywords), set(candidate.keywords)
    min_count, max_count = map(
        lambda func: func(len(main_kw), len(candidate_kw)),
        (min, max)
    )
    miss_weight = 1 / max_count / 2
    match_weight = (1 - miss_weight * (max_count - min_count)) / min_count
    common_count = len(main_kw & candidate_kw)
    score = common_count * match_weight
    return score


def _get_contradiction_score(main, candidate):
    # TODO(cmiN): Implementation.
    return 1.0


def get_bias_score(main, candidate):
    """Returns a tuple of (status, score) telling if the articles are similar and
    opposed and with what score.
    """
    similarity_score = _get_similarity_score(main, candidate)
    if similarity_score < THRES_SIMILARITY:
        return False, 0

    contradiction_score = _get_contradiction_score(main, candidate)
    if contradiction_score < THRES_CONTRADICTION:
        return False, 0

    return True, (similarity_score + contradiction_score) / 2
