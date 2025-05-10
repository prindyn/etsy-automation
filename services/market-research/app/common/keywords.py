import re
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from typing import List, Dict


class KeywordExtractor:
    def __init__(
        self,
        top_n: int = 50,
        ngram_range=(1, 2),
        use_noun_chunks_filter: bool = False,
    ):
        self.top_n = top_n
        self.ngram_range = ngram_range
        self.use_noun_chunks_filter = use_noun_chunks_filter
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=self.ngram_range,
            token_pattern=r"\b\w{2,}\b",
            max_features=1000,
            lowercase=True,
        )
        self.nlp = spacy.load("en_core_web_sm")

    def extract(self, titles: List[str], exclude: str = "") -> List[Dict[str, float]]:
        # Step 1: Compute TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        scores = tfidf_matrix.sum(axis=0).A1
        terms = self.vectorizer.get_feature_names_out()

        # Step 2: Normalize exclude list
        exclude_words = set(w.lower() for w in re.findall(r"\b\w{2,}\b", exclude))

        keyword_scores = {}
        for kw, score in zip(terms, scores):
            # Skip excluded keywords
            if any(word in exclude_words for word in kw.split()):
                continue

            word_count = len(kw.split())
            char_len = len(kw)

            # More weight for longer, more specific keywords
            adjusted_score = score * (1 + 0.15 * word_count) * (1 + 0.05 * char_len)
            keyword_scores[kw] = adjusted_score

        if self.use_noun_chunks_filter:
            noun_chunks = set()
            for title in titles:
                doc = self.nlp(title)
                noun_chunks.update(
                    chunk.text.lower().strip().replace("-", " ")
                    for chunk in doc.noun_chunks
                )
            keyword_scores = {
                kw: score for kw, score in keyword_scores.items() if kw in noun_chunks
            }

        ranked = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return [{"keyword": k, "score": round(v, 4)} for k, v in ranked[: self.top_n]]
