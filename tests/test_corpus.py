from pathlib import Path
from spacy_ebooks.corpus import Corpus

corpus = Corpus("resources", serialize=True)


def test_single_file_corpus():
    c = Corpus("resources/a-merritt_the-moon-pool_advanced.epub3")
    assert len(c.books) == 1


def test_corpus_load():
    assert len(corpus.books) == 2


def test_corpus_book_load():
    for book, expected_path, expected_length in zip(
        corpus,
        [
            Path("resources/a-merritt_the-moon-pool_advanced.epub3"),
            Path(
                "resources/gustave-flaubert_short-fiction_m-walter-dunne_advanced.epub3"
            ),
        ],
        [35, 4],
    ):
        assert len(list(book.structure)) == expected_length
        assert book.file_path == expected_path


def test_standard_ebooks_load():
    # Values current as of 2021/02/02 with the assumption that changes are additive.
    c = Corpus(Path("resources/standard-ebooks"))
    assert len(list(c.books)) >= 629
    assert len(c.author_idx) > 0
    assert len(c.by_genre("Science Fiction")) >= 39
    assert len(c.by_author("Anton Chekhov")) >= 3
    non_ascii_list = c.non_ascii_list()
    assert non_ascii_list
    print(non_ascii_list)

    for book in c:
        path = book.file_path.with_suffix(".txt")
        print(f"Writing {path}...")
        with open(path, "w") as f:
            text = book.text()
            assert len(text) > 100
            f.write(book.text())
