from typing import List, Dict
import requests
from lxml import etree as ElementTree
import spacy
from .matching import load_key_phrase_matcher
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

    key_phrases = {"SEARCH": [search_title.lower()]}
    exact_matcher = load_key_phrase_matcher(nlp, key_phrases, "exact")
    fuzzy_matcher = load_key_phrase_matcher(nlp, key_phrases, "fuzzy")
    similarity_matcher = load_key_phrase_matcher(nlp, key_phrases, "similarity")

    results = []
    for item in root.iter("item"):
        episode_title = item.find("title").text
        cleaned_title = clean_title(episode_title)
        cleaned_title_tokens = tokenize_and_remove_stop_words(cleaned_title, nlp)

        doc = nlp(cleaned_title.lower())

        exact_matches = exact_matcher.matcher(doc)
        fuzzy_matches = fuzzy_matcher.matcher(doc)
        similarity_matches = similarity_matcher.matcher(doc)

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