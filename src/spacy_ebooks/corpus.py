from collections import defaultdict
from pathlib import Path
from typing import Iterator, List
from .book import Book


class Corpus(object):
    """Corpus convenience class for processing a collection of ebooks.

    USAGE:
        >>> from spacy_ebooks.corpus import Corpus
        >>> from collections import Counter
        >>> corpus = Corpus("resources/")
        >>> for book in corpus:
        >>>     print(book.title, book.category, Counter(book.iter_tokens()).most_common(15))"""

    def __init__(self, corpus_path, serialize=False):
        self.corpus_path = Path(corpus_path)
        if not self.corpus_path.exists():
            raise Exception(f"Given corpus path {self.corpus_path} does not exist.")
        if self.corpus_path.is_dir():
            # We keep the books in sorted filename order as tests rely on a deterministic ordering.
            book_files = sorted(self.corpus_path.glob("*.epub*"))
        else:
            book_files = [self.corpus_path]
        self.books = [Book(ebook, serialize=serialize) for ebook in book_files]
        self.author_idx = defaultdict(set)
        self.title_idx = defaultdict(set)
        self.genre_idx = defaultdict(set)
        for idx, book in enumerate(self.books):
            m = book.metadata
            if "author" in m:
                self.author_idx[m["author"]].add(idx)
            if "title" in m:
                self.title_idx[m["title"]].add(idx)
            if "genre" in m:
                self.genre_idx[m["genre"]].add(idx)

    def __iter__(self) -> Iterator[Book]:
        for book in self.books:
            yield book

    def __getitem__(self, index: int) -> Book:
        return self.books[index]

    def by_author(self, author: str) -> List[Book]:
        return [self.books[idx] for idx in self.author_idx[author]]

    def by_title(self, title: str) -> List[Book]:
        return [self.books[idx] for idx in self.title_idx[title]]

    def by_genre(self, genre: str) -> List[Book]:
        return [self.books[idx] for idx in self.genre_idx[genre]]
