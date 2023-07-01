from typing import List, Dict
import requests
from lxml import etree as ElementTree
import spacy
from spacy.matcher import PhraseMatcher
from spaczz.matcher import SimilarityMatcher, FuzzyMatcher
from .matching import BaseMatcher, ExactMatcher, SimMatcher, FuzzMatcher
from .lookup_podcast import tokenize_and_remove_stop_words, clean_title, spacy_similarity



class SearchResult:
    def __init__(self, title, url, score):
        self.title = title
        self.url = url
        self.score = score

    def __lt__(self, other):
        return self.score > other.score


def search_episodes_by_title(rss_feed_url: str, search_title: str, max_results: int = 10):
    response = requests.get(rss_feed_url)
    root = ElementTree.fromstring(response.content)
    nlp = spacy.load("en_core_web_sm")

    search_title_tokens = tokenize_and_remove_stop_words(search_title, nlp)

    exact_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    exact_matcher.add("SEARCH", [nlp(search_title.lower())])

    fuzzy_matcher = FuzzyMatcher(nlp.vocab, min_r1=80, min_r2=90)
    fuzzy_matcher.add("SEARCH", [nlp(search_title)])

    sim_matcher = SimilarityMatcher(nlp.vocab, min_r1=80, min_r2=90)
    sim_matcher.add("SEARCH", [nlp(search_title)])

    results = []
    for item in root.iter("item"):
        episode_title = item.find("title").text
        cleaned_title = clean_title(episode_title)
        cleaned_title_tokens = tokenize_and_remove_stop_words(cleaned_title, nlp)

        doc = nlp(cleaned_title.lower())
        exact_matches = exact_matcher(doc)
        fuzzy_matches = fuzzy_matcher(doc)
        similarity_matches = sim_matcher(doc)

        if exact_matches:
            score = 1.0
        elif fuzzy_matches:
            score = fuzzy_matches[0].ratio / 100
        else:
            similarity = spacy_similarity(search_title_tokens, cleaned_title_tokens, nlp)
            score = similarity

        enclosure = item.find("enclosure")
        if enclosure is not None:
            results.append(SearchResult(cleaned_title, enclosure.attrib["url"], score))

    results.sort()
    return [{"title": res.title, "url": res.url, "score": res.score} for res in results[:max_results]]