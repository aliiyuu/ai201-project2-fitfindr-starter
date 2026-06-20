# tests/test_tools.py
from tools import search_listings

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_search_no_filters_returns_matches():
    # With no size/price limits, a common keyword should return several items.
    results = search_listings("vintage", size=None, max_price=None)
    assert len(results) > 1
    assert all("vintage" in (
        item["title"] + item["description"] + " ".join(item["style_tags"])
    ).lower() for item in results)


def test_search_description_is_case_insensitive():
    lower = search_listings("denim jacket", size=None, max_price=None)
    upper = search_listings("DENIM JACKET", size=None, max_price=None)
    assert [item["id"] for item in lower] == [item["id"] for item in upper]


def test_search_size_filter_substring_match():
    # "M" should match listings whose size string contains it, e.g. "S/M".
    results = search_listings("top", size="M", max_price=None)
    assert len(results) > 0
    assert all("m" in item["size"].lower() for item in results)


def test_search_size_filter_excludes_nonmatching():
    # A specific waist size should only return bottoms with that token
    results = search_listings("pants", size="W29", max_price=None)
    assert all("w29" in item["size"].lower() for item in results)


def test_search_results_sorted_by_relevance():
    # More keyword overlap should rank higher; scores must be non-increasing
    results = search_listings("vintage graphic tee", size=None, max_price=None)

    def score(item):
        text = (
            item["title"] + item["description"] + " ".join(item["style_tags"])
        ).lower()
        return sum(w in text for w in ["vintage", "graphic", "tee"])

    scores = [score(item) for item in results]
    assert scores == sorted(scores, reverse=True)


def test_search_zero_score_items_dropped():
    # Every returned item must match at least one keyword
    results = search_listings("cargo", size=None, max_price=None)
    assert all("cargo" in (
        item["title"] + item["description"] + " ".join(item["style_tags"])
    ).lower() for item in results)


def test_search_returns_full_listing_dicts():
    results = search_listings("denim", size=None, max_price=None)
    assert len(results) > 0
    expected_keys = {
        "id", "title", "description", "category", "style_tags", "size",
        "condition", "price", "colors", "brand", "platform",
    }
    assert expected_keys.issubset(results[0].keys())