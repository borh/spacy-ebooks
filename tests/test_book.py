from pathlib import Path
from spacy_ebooks.book import Book, Paragraph


def test_nlp():
    test_strings = ["would—what", "would\u2060—what"]

    assert len(list(Paragraph.nlp(test_strings[0]))) == 3
    # The test below should work as the \u2060 (Unicode Character 'WORD JOINER' (U+2060)) is present, but in reality, we would want this to be three tokens.
    assert len(list(Paragraph.nlp(test_strings[1]))) == 1


def test_book_load():
    book = Book(Path("resources/abraham-merritt_the-moon-pool.epub3"))
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
        assert paragraph.sentences() == [s for s in paragraph]
        assert len(paragraph.sentences()) > 0
        for sentence in paragraph:
            assert sentence.text is not ""
            assert len(list(sentence)) > 0

    for sentence in book.sentences():
        assert str(sentence) == sentence.text
        # print(sentence)  # ._.emphasis_spans)
