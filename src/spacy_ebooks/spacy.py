import spacy


class EbookPipeline:
    """spaCy ebook pipeline intended for use in spacy-ebooks package. Its main purpose
    is to adjust some of spaCy's default to make it more suitable for ebook-style
    tokenization and add ebook metadata to the Doc (new entities, etc.)."""

    def __init__(self, nlp, **cfg):
        self.nlp = nlp

    def __call__(self, doc):
        # retokenize doc, etc...
        return doc
