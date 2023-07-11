from pathlib import Path
from spacy_ebooks.book import Book


def test_book_load():
    book = Book(Path("resources/a-merritt_the-moon-pool_advanced.epub"))
    # print(list(str(p) for p in list(book.paragraphs())[0:5]))
    # for part in book:
    #     # Short-circuit below by specifying level here (i.e. change parts() to sentences())
    #     for section in part:
    #         for chapter in section:
    #             for paragraph in chapter:
    #                 for sentence in paragraph:
    #                     print(section, chapter, paragraph, sentence)

    # Get all emphasized text in the book:
    assert len(list(book.paragraphs())) > 0
    for paragraph in book.paragraphs():
        assert len(paragraph.doc()) == 2
        assert len(paragraph.text()) > 0
        # print(sentence)  # ._.emphasis_spans)

    for text_window in book.text_partitions(10):
        print(text_window)
        assert len(text_window) == 10
        break


def test_book_parsing():
    book = Book(
        Path("resources/fantasy/arthur-conan-doyle_the-lost-world_advanced.epub"),
        serialize=True,
    )
    paragraphs = list(book.paragraphs())
    assert (
        paragraphs[2].text()
        == """Mr. Hungerton, her father, really was the most tactless person upon earth—a fluffy, feathery, untidy cockatoo of a man, perfectly good-natured, but absolutely centered upon his own silly self. If anything could have driven me from Gladys, it would have been the thought of such a father-in-law. I am convinced that he really believed in his heart that I came round to the Chestnuts three days a week for the pleasure of his company, and very especially to hear his views upon bimetallism, a subject upon which he was by way of being an authority."""
    )
