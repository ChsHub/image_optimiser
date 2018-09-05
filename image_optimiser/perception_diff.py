from difflib import SequenceMatcher


def is_similar_fit(a, b):
    similarity = SequenceMatcher(None, a, b).ratio()
    if similarity >= 0.85:
        # print("#ACCEPT " + str(similarity))
        return True
    return False