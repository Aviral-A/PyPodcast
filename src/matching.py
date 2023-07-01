from typing import List, Dict

import requests
from lxml import etree as ElementTree
import spacy

from spacy.matcher import PhraseMatcher
from spaczz.matcher import SimilarityMatcher, FuzzyMatcher

class BaseMatcher:
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.nlp_engine = nlp_engine
        self.keyphrase_id, self.keyphrase_categ = {}, {}
        for category in categories:
            for phrase in keyphrases[category]:
                self._add_phrase(phrase, category)

    def _add_phrase(self, phrase, category):
        raise NotImplementedError

    def update_categories(self, categories: List[str]):
        for category in set(self.keyphrase_categ.values()):
            if category not in categories:
                for phrase in [item for item, cat in self.keyphrase_categ.items() if cat == category]:
                    self._remove_phrase(phrase)

    def _remove_phrase(self, phrase):
        raise NotImplementedError

class ExactMatcher(BaseMatcher):
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.matcher = PhraseMatcher(nlp_engine.vocab, attr="LOWER")
        super().__init__(nlp_engine, keyphrases, categories)

    def _add_phrase(self, phrase, category):
        self.matcher.add(phrase[0], [self.nlp_engine(phrase[0])])
        self.keyphrase_id[phrase[0]] = phrase[1]
        self.keyphrase_categ[phrase[0]] = category

    def _remove_phrase(self, phrase):
        self.matcher.remove(phrase)

class SimMatcher(BaseMatcher):
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.matcher = SimilarityMatcher(nlp_engine.vocab, min_r1=80, min_r2=90)
        super().__init__(nlp_engine, keyphrases, categories)

    def _add_phrase(self, phrase, category):
        self.matcher.add(phrase[0], [self.nlp_engine(phrase[0])])
        self.keyphrase_id[phrase[0]] = phrase[1]
        self.keyphrase_categ[phrase[0]] = category

    def _remove_phrase(self, phrase):
        self.matcher.remove(phrase)

class FuzzMatcher(BaseMatcher):
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.matcher = FuzzyMatcher(nlp_engine.vocab, min_r1=80, min_r2=90)
        super().__init__(nlp_engine, keyphrases, categories)

    def _add_phrase(self, phrase, category):
        self.matcher.add(phrase[0], [self.nlp_engine(phrase[0])])
        self.keyphrase_id[phrase[0]] = phrase[1]
        self.keyphrase_categ[phrase[0]] = category

    def _remove_phrase(self, phrase):
        self.matcher.remove(phrase)

def load_key_phrase_matcher(nlp, key_phrases, match_type):
    if match_type == "similarity":
        key_phrase_matcher = SimMatcher(nlp, key_phrases, key_phrases.keys())
    elif match_type == "fuzzy":
        key_phrase_matcher = FuzzMatcher(nlp, key_phrases, key_phrases.keys())
    else:
        key_phrase_matcher = ExactMatcher(nlp, key_phrases, key_phrases.keys())
    return key_phrase_matcher

def tokenize_and_remove_stop_words(title: str, nlp) -> List[str]:
    doc = nlp(title.lower())
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return tokens

def spacy_similarity(title1: str, title2: str, nlp) -> float:
    doc1 = nlp(" ".join(title1))
    doc2 = nlp(" ".join(title2))
    return doc1.similarity(doc2)

def clean_title(title: str) -> str:
    return title.strip()

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
    return [{"title": res.title, "url": res.url} for res in results[:max_results]]