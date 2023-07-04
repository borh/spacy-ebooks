from pathlib import Path
from spacy_ebooks.book import Book, Paragraph


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
