# app/utils/ner.py

import re
from transformers import pipeline

# Load one time
ner_model = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

def clean_entity(text: str) -> str:
    """
    Cleans tokenization artifacts and normalizes formatting.
    """
    if not text:
        return ""

    text = text.replace("##", "")         # remove BERT artifacts
    text = text.strip()

    # Remove stray punctuation
    text = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", text)

    # Normalize casing (Apple, California, Elon Musk)
    if len(text) <= 1:
        return ""  # Remove single-letter noise such as 'El'

    return text.title()


def extract_entities(text: str) -> dict:
    """
    Extract structured entities from raw text with cleanup.
    Returns:
    {
        "people": [...],
        "organizations": [...],
        "locations": [...],
        "products": [...],  # loosely inferred
    }
    """

    if not text:
        return {
            "people": [],
            "organizations": [],
            "locations": [],
            "products": [],
        }

    ner_results = ner_model(text)

    people = set()
    orgs = set()
    locs = set()
    prods = set()  # not native — heuristic

    for ent in ner_results:
        raw = ent["word"]
        clean = clean_entity(raw)
        if not clean:
            continue

        if ent["entity_group"] == "PER":
            people.add(clean)

        elif ent["entity_group"] == "ORG":
            # remove common false-positives like “El”
            if len(clean) > 2:
                orgs.add(clean)

        elif ent["entity_group"] == "LOC":
            locs.add(clean)

        elif ent["entity_group"] in ("MISC",):
            # treat proper nouns as products (light heuristic)
            if clean.lower() not in ["news", "report"]:
                prods.add(clean)

    return {
        "people": sorted(people),
        "organizations": sorted(orgs),
        "locations": sorted(locs),
        "products": sorted(prods),
    }