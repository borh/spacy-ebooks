import spacy

nlp = spacy.blank("en")
nlp.add_pipe(
        "llm",
        config={
            "task": {
                "@llm_tasks": "spacy.NER.v2",
                "labels": ["PERSON", "ORGANISATION", "LOCATION", "TIME"]
                # CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART
            },
            "backend": {
                "@llm_backends": "spacy.StableLM_HF.v1",
                "model": "stabilityai/stablelm-tuned-alpha-3b",
                # "@llm_backends": "spacy.OpenLLaMa_HF.v1", # "spacy.REST.v1",
                # "model": "openlm-research/open_llama_3b_600bt_preview",
                # "api": "OpenAI",
                # "config": {"model": "gpt-3.5-turbo"},
            },
            "cache": {
                "@llm_misc": "spacy.BatchCache.v1",
                "path": "cache",
                "batch_size": 64,
                "max_batches_in_mem": 4,
            }
        },
    )
nlp.initialize()

def llm_ner(s):
    doc = nlp(s)
    return [(ent.text, ent.label_) for ent in doc.ents]
