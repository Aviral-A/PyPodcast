from typing import List, Dict
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
                phrases_to_remove = [item for item, cat in self.keyphrase_categ.items() if cat == category]
                for phrase in phrases_to_remove:
                    self._remove_phrase(phrase)

    def _remove_phrase(self, phrase):
        raise NotImplementedError

class MatcherMixin:
    def _add_phrase(self, phrase, category):
        self.matcher.add(phrase[0], [self.nlp_engine(phrase[0])])
        self.keyphrase_id[phrase[0]] = phrase[1]
        self.keyphrase_categ[phrase[0]] = category

    def _remove_phrase(self, phrase):
        self.matcher.remove(phrase)

class ExactMatcher(BaseMatcher, MatcherMixin):
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.matcher = PhraseMatcher(nlp_engine.vocab, attr="LOWER")
        super().__init__(nlp_engine, keyphrases, categories)

class SimMatcher(BaseMatcher, MatcherMixin):
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.matcher = SimilarityMatcher(nlp_engine.vocab, min_r1=80, min_r2=90)
        super().__init__(nlp_engine, keyphrases, categories)

class FuzzMatcher(BaseMatcher, MatcherMixin):
    def __init__(self, nlp_engine, keyphrases: Dict[str, List[str]], categories: List[str]):
        self.matcher = FuzzyMatcher(nlp_engine.vocab, min_r1=80, min_r2=90)
        super().__init__(nlp_engine, keyphrases, categories)

def load_key_phrase_matcher(nlp, key_phrases, match_type):
    matcher_classes = {"similarity": SimMatcher, "fuzzy": FuzzMatcher, "exact": ExactMatcher}
    key_phrase_matcher = matcher_classes.get(match_type, ExactMatcher)(nlp, key_phrases, key_phrases.keys())
    return key_phrase_matcher