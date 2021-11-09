from pathlib import Path
from spacy_ebooks.corpus import Corpus

corpus = Corpus("resources", serialize=True)


def test_single_file_corpus():
    c = Corpus("resources/abraham-merritt_the-moon-pool.epub3")
    assert len(c.books) == 1


def test_corpus_load():
    assert len(corpus.books) == 2


def test_corpus_book_load():
    for book, expected_path, expected_length in zip(
        corpus,
        [
            Path("resources/abraham-merritt_the-moon-pool.epub3"),
            Path("resources/gustave-flaubert_short-fiction.epub3"),
        ],
        [35, 4],
    ):
        print(book.structure)
        assert len(list(book.structure)) == expected_length
        assert book.file_path == expected_path


def test_standard_ebooks_load():
    c = Corpus(Path("resources/standard-ebooks"))
    assert len(list(c.books)) == 278
    assert len(c.author_idx) > 0
    assert len(c.by_genre("Science Fiction")) == 18
    assert len(c.by_author("Anton Chekhov")) == 2
