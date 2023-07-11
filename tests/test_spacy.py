import multiprocessing
from spacy_ebooks.book import Book, Paragraph
from spacy_ebooks.llm import llm_ner
from pathlib import Path
import spacy
from spacy.tokens import DocBin
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")


def test_tokenization():
    test_strings = [
        "would—what",
        "would\u2060—what",
        "Here was a mystery—a mystery indeed! Lakla softly closed the crimson stone.",
    ]
    paragraphs = [Paragraph({"text": s}) for s in test_strings]

    for paragraph, tokens, sentences in zip(paragraphs, [3, 1, 16], [1, 1, 2]):
        doc = nlp(paragraph.text())
        print([t for t in doc])
        assert len(doc) == tokens
        assert len(list(doc.sents)) == sentences

    # assert len(list(Paragraph.nlp(test_strings[0]))) == 3
    # # The test below should work as the \u2060 (Unicode Character 'WORD JOINER' (U+2060)) is present, but in reality, we would want this to be three tokens.
    # assert len(list(Paragraph.nlp(test_strings[1]))) == 1


matcher = Matcher(nlp.vocab)
pattern = [
    {"POS": {"IN": ["NOUN", "SYM", "VERB"]}, "OP": "+"},
    {"TEXT": {"REGEX": r".*"}, "OP": "?"},
]
matcher.add("Nouns", [pattern])


def test_spacy():
    b = Book(Path("resources/a-merritt_the-moon-pool_advanced.epub"))
    for doc in nlp.pipe(b.paragraph_meta_tuples(), as_tuples=True):
        assert len(doc) > 0


import time


def test_spacy_cached():
    b = Book(Path("resources/a-merritt_the-moon-pool_advanced.epub"))
    cache_filename = Path(b.file_path.name + ".spacy")
    if not cache_filename.exists():
        start_time = time.time()
        docs = list(nlp.pipe(p.text() for p in b.paragraphs()))
        doc_bin = DocBin(docs=docs, store_user_data=True)
        doc_bin.to_disk(cache_filename)
        print("--- %s seconds --- DocBin creation" % (time.time() - start_time))
    docs = list(DocBin().from_disk(cache_filename).get_docs(nlp.vocab))
    assert len(docs) == 2493

    for _ in range(8):
        docs += docs
    print(docs[0:3])
    matches = []
    start_time = time.time()
    for doc in docs:
        ms = matcher(doc)
        matches.extend(m[1:] for m in ms)
    print("--- %s seconds --- Serial match" % (time.time() - start_time))
    print(matches[:10])
    assert len(matches) == 17949


# import concurrent.futures
# from multiprocessing import Pool, Process, get_context
# from loky import get_reusable_executor
# from itertools import chain, islice
#
#
# def iter_chunks(iterable, n):
#     """[list(chunk) for chunk in iter_chunks(iter(range(20)), 3)]
#     [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17], [18, 19]]"""
#     it = iter(iterable)
#     while True:
#         chunk = tuple(islice(it, n))
#         if not chunk:
#             return
#         yield chunk
#
#
# def doc_match(doc):
#     ms = matcher(doc)
#     return [m[1:] for m in ms]
#
#
# def parallel_match(docs):
#     print("parallel_match", len(docs))
#     return [
#         ms
#         for doc in docs
#         for ms in doc_match(doc)
#         # for m in ms
#     ]
#
#
# def test_spacy_parallel():
#     b = Book(Path("resources/a-merritt_the-moon-pool_advanced.epub"))
#     cache_filename = Path(b.file_path.name + ".spacy")
#     if not cache_filename.exists():
#         docs = list(nlp.pipe(p.text() for p in b.paragraphs()))
#         doc_bin = DocBin(docs=docs, store_user_data=True)
#         doc_bin.to_disk(cache_filename)
#
#     start_time = time.time()
#     docs = list(DocBin().from_disk(cache_filename).get_docs(nlp.vocab))
#     print("--- %s seconds --- DocBin load" % (time.time() - start_time))
#     print(len(docs))
#
#     for _ in range(8):
#         docs += docs
#     print(docs[0:3])
#     print(len(docs))
#     matches = []
#     thread_count = multiprocessing.cpu_count() - 2
#     chunk_size = len(docs) // thread_count
#     if chunk_size < 50000:
#         chunk_size = 50000
#     doc_iter = list(iter_chunks(docs, chunk_size))
#     print(len(doc_iter), [len(c) for c in doc_iter])
#
#     start_time = time.time()
#     # # with Pool(processes=24) as pool:
#     # with get_context("fork").Pool() as pool:
#     #      results = [pool.apply_async(parallel_match, (chunk,)) for chunk in doc_iter]
#     #      for r in results:
#     #          r.wait()
#     #      for result in results:
#     #          ms = result.get()
#     #          if len(ms) > 0:
#     #              matches.extend(ms)
#
#     # matches.extend(chain.from_iterable(
#     #     m
#     #     for m in pool.imap(parallel_match, doc_iter, chunksize=1)
#     #     if len(m) > 0
#     # ))
#     # with get_reusable_executor(max_workers=thread_count) as executor:
#     with concurrent.futures.ProcessPoolExecutor(max_workers=thread_count) as executor:
#         futures = []
#         for chunk in doc_iter:
#             futures.append(executor.submit(parallel_match, chunk))
#
#         concurrent.futures.wait(futures)
#         for future in futures:
#             # for future, _ in concurrent.futures.wait(futures): # as_completed(futures):
#             ms = future.result()
#             if len(ms) > 0:
#                 matches.extend(ms)
#         # matches.extend(chain.from_iterable(m for m in executor.map(parallel_match, docs, chunksize=500) if m))
#     print("--- %s seconds --- Parallel match" % (time.time() - start_time))
#
#     print(matches[:10])
#
#     assert len(matches) == 17949

def test_llm_ner():
    r = llm_ner("Jack and Jill rode up the hill in Les Deux Alpes")
    print(r)
    assert len(r) == 1
    assert len(r[0][0]) > 1
