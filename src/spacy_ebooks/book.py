from copy import deepcopy

import ebooklib
from ebooklib import epub

# from spacy.tokens import Doc
import re
from pathlib import Path
from lxml import etree
from io import BytesIO
from itertools import chain, takewhile, count, islice
import json
from typing import Iterator, Dict, List

# import spacy
# from spacy.tokens import Token

import logging

log = logging.getLogger("ebook_logger")

# TODO hyphens, quotation marks etc. https://github.com/explosion/spaCy/issues/4384

# TODO refactor to exclude spacy usage. This should allow export to TEI as well as (sentence (or paragraph?), context) sequences.
# If we decide to pass paragraphs, we need to be sure that context indexes still map onto document indexes correctly (is this how spacy works??).


def non_overlapping_windows(seq, n):
    """Yield slices of length n from seq."""
    return takewhile(len, (seq[i : i + n] for i in count(0, n)))


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def text_windows(text, window_size=2000):
    for i in range(int(len(text) / window_size)):
        yield text[i * window_size : (i * window_size) + window_size]


def clean_text(s: str | None) -> str | None:
    if s is None:
        return None
    clean_rx = re.compile(r"[\u2060]")
    return clean_rx.sub("", s.replace("\xa0", " "))


def textify(t):
    s = []
    if t.text:
        s.append(t.text)
    for child in t.getchildren():
        s.extend(textify(child))
    if t.tail:
        s.append(t.tail)
    return "".join(s)


# class Sentence(object):
#     def __init__(self, s):
#         self.s = s
#         self.text = s.text
#
#     def __call__(self):
#         return self.s
#
#     def __repr__(self):
#         return f"S='{self.text}'"
#
#     def __str__(self):
#         return self.text
#
#     def to_json(self):
#         return self.text
#
#     def __iter__(self) -> Iterator[Token]:
#         for token in self.s:
#             yield token


class Paragraph(object):

    # nlp = spacy.load("en_core_web_sm")
    # infixes = nlp.Defaults.infixes + (r"(?<=[0-9])–(?=[0-9-])",)
    # print(infixes)
    # suffixes = nlp.Defaults.suffixes + ("―",)
    # print(suffixes)
    # infix_regex = spacy.util.compile_infix_regex(infixes)
    # print(infix_regex.search("would\u2060—what"))
    # suffix_regex = spacy.util.compile_suffix_regex(suffixes)
    # print(suffix_regex.search("would\u2060—what"))
    # nlp.tokenizer.infix_finditer = infix_regex.finditer
    # nlp.tokenizer.suffix_search = suffix_regex.search

    def __init__(self, p, level=None, number=None):
        self._text = p["text"]
        try:
            self._meta = p["meta"]
        except KeyError:
            self._meta = {}
        self._spans = p["spans"] if "spans" in p else None
        self._label = p["label"] if "label" in p else None
        if level:
            self._meta["level"] = level
        if number:
            self._meta["number"] = number
        # self._meta["tags"] = p["tags"] if "tags" in p else []

    # def _process(self):
    #     self.docs = Paragraph.nlp.pipe(self.text)  # , n_process=-1, batch_size=10000)
    #     for doc in self.docs:
    #         for s in doc.sents:
    #             yield Sentence(s)

    # def __iter__(self):
    #     if hasattr(self, "sents"):
    #         for s in self.sents:
    #             yield s
    #     else:
    #         for doc in Paragraph.nlp.pipe(
    #             self.text
    #         ):  # , n_process=-1, batch_size=10000):
    #             for s in doc.sents:
    #                 yield Sentence(s)

    # def sentences(self):
    #     if not hasattr(self, "sents"):
    #         self.sents = list(self._process())

    #     return self.sents

    def to_json(self):
        return (
            {"meta": self._meta, "text": self._text}
            | ({"spans": self._spans} if self._spans else {})
            | ({"label": self._label} if self._label else {})
        )

    def doc(self):
        return (
            self._text,
            self._meta
            | ({"spans": self._spans} if self._spans else {})
            | ({"label": self._label} if self._label else {}),
        )

    def text(self):
        return self._text

    def meta(self):
        return self._meta

    def __len__(self):
        return len(self._text)

    def __str__(self):
        return "<Paragraph meta={} text='{}'>".format(self._meta, self._text)

    def __repr__(self):
        return "<Paragraph meta={} text='{}'>".format(self._meta, self._text)


class BookStructure(object):
    """Conveniance class to represent a book's structure in terms of parts, sections, chapters as well as associated text (paragraphs).
    Includes export (serialization) functionality (currently only TEI and JSON).

    Args:
        list_of_parts (`List`): ..."""

    def __init__(self, list_of_parts: List):
        # TODO this needs to be indexed (which parts correspond to which chapters, etc.) and saved in-order
        # part, section, chapter = None, None, None
        self.parts = []
        self.sections = []
        self.chapters = []
        for l in list_of_parts:
            level = l["level"]
            i = l.get("number", None)
            paragraphs = [Paragraph(p, level, i) for p in l["paragraphs"]]
            if level == "part":
                self.parts.append(paragraphs)
            elif level == "section":
                self.sections.append(paragraphs)
            elif level == "chapter":
                self.chapters.append(paragraphs)
            else:
                # We fallback on the lowest level(?).
                self.chapters.append(paragraphs)
        self.bs = list_of_parts

    def to_json(self):
        return [p for p in self]

    def __iter__(self):
        for ps in chain(self.parts, self.sections, self.chapters):
            yield ps

    # def parts(self):
    #     for part in self.parts:
    #         yield part

    # def sections(self):
    #     for section in self.sections:
    #         yield section

    # def chapters(self):
    #     for chapters in self.sections():
    #         for chapter in chapters:
    #             yield chapter

    def paragraphs(self):
        for paragraphs in self:
            for paragraph in paragraphs:
                yield paragraph

    def paragraph_meta_tuples(self):
        for p in self.paragraphs():
            yield p.doc()

    # def sentences(self):
    #     for paragraph in self.paragraphs():
    #         for sentence in paragraph:
    #             yield sentence

    # def t okens(self, field=None):
    #     for sentence in self.sentences():
    #         for token in sentence:
    #             if field:
    #                 yield getattr(token, field)
    #             else:
    #                 yield token


class Book(object):
    """ebook Doc wrapper for spaCy that preserves structural information (paragraphs, sections, chapters, etc.)
    and other formatting commonly found in books (emphasis: italic or bold) for documents longer than spaCy's models
    can handle in one go. The main interface is a set of iterators over the structure of the book, where each iterator
    will yield another iterator of a structural level below it:

    part > chapter > paragraph (spaCy Doc) > sentence > spaCy tokens

    USAGE:
        >>> from spacy_ebooks.book import Book
        >>> book = Book("path/to/ebook.epub")
        >>> for part in book.parts(): # Short-circuit below by specifying level here (i.e. change parts() to sentences())
        >>>     for section in part:
        >>>         for chapter in section:
        >>>             for paragraph in chapter:
        >>>                 for sentence in paragraph:
        >>>                     print(section, chapter, paragraph.id, sentence.id, sentence)

        >>> # Get all emphasized text in the book:
        >>> for sentence in book.sentences():
        >>>     print(sentence._.emphasis_spans)"""

    name = "book"

    def __init__(self, file_path: Path, serialize: bool = False):
        self.file_path = file_path
        # if not Doc.has_extension("book_metadata"):
        #     Doc.set_extension("book_metadata", getter=self.get_metadata)
        # if not Doc.has_extension("emphasis_spans"):
        #     Doc.set_extension("emphasis_spans", getter=self.get_emphasis_spans)
        e = epub.read_epub(file_path)
        self.metadata = {}
        for d in self.parse_metadata(e.metadata):
            for k, v in d.items():
                if k in self.metadata:
                    if isinstance(self.metadata[k], str):
                        self.metadata[k] = [self.metadata[k], v]
                    else:
                        self.metadata[k].append(v)
                else:
                    self.metadata[k] = v

        log.info(f"Processing {self.metadata}.")
        self.structure = self.parse_structure(e)

        if serialize:
            with open(Path(self.file_path.with_suffix(".json")), "w") as f_json, open(
                Path(self.file_path.with_suffix(".txt")), "w"
            ) as f_txt:
                json.dump(
                    self.structure,
                    f_json,
                    ensure_ascii=False,
                    default=lambda x: x.to_json()
                    if hasattr(x, "to_json")
                    else x.__dict__,
                    indent=4,
                )
                f_txt.write(self.text())

    # def __call__(
    #     self, doc: Doc
    # ) -> Doc:  # TODO should we be calling this as doc wrapper??
    #     return doc

    @staticmethod
    def _infer_structure(s):
        """Infers which parts of the ebook to extract and which to ignore based on their filenames.
        This list is not comprehensive, and may need to be updated depending on the ebook used.
        Unrecognized filenames will be extracted (not ignored)."""
        s = s.replace(".xhtml", "")
        extract_parts = ["prelude", "act", "book", "chapter", "part"]
        ignore_parts = [
            "appendix",
            "colophon",
            "dedication",
            "dramatis-personae",
            "endnotes",  # This should be included? (there are footnote references in text)
            "epigraph",
            "epilogue",
            "foreword",
            "glossary",
            "halftitle",
            "imprint",
            "introduction",
            "loi",
            "note",
            "preamble",
            "preface",
            "prologue",
            "the-persons-of-the-play",
            "titlepage",
            "uncopyright",
        ]
        extract_re = re.compile(r"({})-([\d\-]+)".format("|".join(extract_parts)))
        ignore_re = re.compile(r"({})".format("|".join(ignore_parts)))
        m = extract_re.match(s)
        if m:
            return {
                "level": m.group(1),
                "number": int(m.group(2))
                if re.match(r"\d+$", m.group(2))
                else m.group(2),  # FIXME maybe stick with strings?
            }
        elif ignore_re.match(s):
            return False
        else:
            return {"level": "unknown", "name": s}

    @staticmethod
    def attribute_map(kvs, tag):
        key_tr = {
            "abbr": None,
            "href": None,
            "i": "i",
            "lang": "language",
            "id": "identifier",
            "class": "class",
            "em": "emphasis",
            "epub:type": "entity_type",
            "h3": "header",
        }
        m = {}
        for k, v in kvs.items():
            sanitized_k = re.sub(r"{[^}]+}", "", k)
            inferred_k = key_tr.get(sanitized_k)
            if inferred_k:
                m[inferred_k] = v
        if len(m) == 0:
            inferred_tag = key_tr.get(tag)
            if inferred_tag:
                m["type"] = inferred_tag
            # FIXME: map z\d\d\d\d in v to something: https://www.daisy.org/z3998/2012/z3998-2012.html
        return ",".join(v for _, v in m.items())

    @staticmethod
    def tag_map(tag):
        return {"em": "emphasis"}

    def parse_structure(self, e):
        """Parses all HTML files that contain the main text into data structures representing metadata-tagged text
        segmented into book parts and paragraphs. Sentence segmentation is not conducted."""
        structure = list()
        for item in e.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if item.is_chapter():
                t = item.get_id().lower()
                level_info = self._infer_structure(t)
                if level_info == "unknown":
                    print(f"{level_info} t={t} item={item}")
                    continue
                elif not level_info:
                    continue
                body = item.get_body_content()
                # We set the standard start and end events, even though we do not
                # dispatch on start. Leaving start out, however, breaks the code.
                context = etree.iterparse(
                    BytesIO(body), events=("start", "end"), recover=True
                )
                d = []
                for action, element in context:
                    if action == "end" and re.match(r"p|h\d", element.tag):
                        paragraph = {"text": "", "meta": {}}
                        if element.text:
                            paragraph["text"] += clean_text(element.text)
                        # We roughly follow spaCy/prodigy annotation data structure: https://prodi.gy/docs/api-interfaces
                        # Add classification labels:
                        is_tagged = self.attribute_map(element.attrib, element.tag)
                        if len(is_tagged) > 0:
                            paragraph["label"] = is_tagged
                        for child in element:
                            start = len(paragraph["text"])
                            if child.text:
                                paragraph["text"] += clean_text(child.text)
                            end = len(paragraph["text"])
                            is_valid_label = self.attribute_map(child.attrib, child.tag)
                            if len(is_valid_label) > 0:
                                paragraph["spans"] = paragraph.get("spans", []) + [
                                    {
                                        "text": clean_text(child.text) or "",
                                        "start": start,
                                        "end": end,
                                        "label": is_valid_label,
                                    }
                                ]
                            if child.tail:
                                paragraph["text"] += clean_text(child.tail)

                        if paragraph["text"].strip() != "":
                            d.append(paragraph)
                    continue

                level_info["paragraphs"] = d
                if (
                    len(level_info["paragraphs"]) > 0
                    and len(level_info["paragraphs"][0]["text"]) > 0
                ):
                    structure.append(level_info)

        assert len(structure) > 0

        return BookStructure(structure)

    @staticmethod
    def parse_metadata(e):
        try:
            tuples = e["http://www.idpf.org/2007/opf"][None]
            for a, b in tuples:
                if b == {"property": "se:subject"}:
                    yield {"genre": a}
                elif b == {"property": "file-as", "refines": "#title"}:
                    yield {"title": a}
                # FIXME sometimes this describes the cover artist
                # elif b == {
                #     "property": "se:name.person.full-name",
                #     "refines": "#author",
                #     }:
                #     yield {"fullname": a}
                elif b == {"property": "file-as", "refines": "#author"}:
                    yield {"shortname": a}
        except KeyError:
            pass

        purl = e["http://purl.org/dc/elements/1.1/"]
        for a, b in purl["creator"]:
            if b == {"id": "author"}:
                yield {"author": a}
        for a, b in purl["subject"]:
            yield {"subjects": a}

    def get_metadata(self):
        return self.metadata

    def title(self):
        return self.metadata["title"]

    def author(self):
        return self.metadata["author"]

    def genre(self):
        return self.metadata["genre"]

    def __repr__(self):
        return f"Book({self.metadata})"

    def get_emphasis_spans(self):
        return {}

    def iter_section(self):
        for section in self.structure.sections:
            yield section

    def iter_level(self, level):
        """Iterate book at given level (part, section, chapter, paragraph)."""
        pass

    def __getitem__(self, index):
        return self.structure[index]

    def __iter__(self):
        for part in self.structure:
            yield part

    # def sentences(self):
    #     return self.structure.sentences()

    def by_section(self, as_tuples=False):
        for section in self.structure.chapters:
            if as_tuples:
                yield section.paragraph_meta_tuples()
            else:
                yield section.paragraphs()

    def paragraphs(self):
        return self.structure.paragraphs()

    def paragraph_meta_tuples(self):
        return self.structure.paragraph_meta_tuples()

    def text(self):
        return "\n".join(p.text() for p in self.paragraphs())

    def text_partitions(self, window_size=2000):
        return text_windows(self.text(), window_size=window_size)
