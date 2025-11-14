# app/services/entity_service.py

from app.utils.ner import extract_entities
from app.db.models import ArticleEntity
from datetime import datetime

def process_entities_for_article(article, db):
    """Extract and store entities for a single article."""

    # Avoid duplicates — skip if already processed
    if article.entities and len(article.entities) > 0:
        return

    entities = extract_entities(article.title or "")

    batches = []

    for e in entities["people"]:
        batches.append(ArticleEntity(
            article_id=article.id,
            entity=e,
            entity_type="person"
        ))

    for e in entities["organizations"]:
        batches.append(ArticleEntity(
            article_id=article.id,
            entity=e,
            entity_type="organization"
        ))

    for e in entities["locations"]:
        batches.append(ArticleEntity(
            article_id=article.id,
            entity=e,
            entity_type="location"
        ))

    for e in entities["products"]:
        batches.append(ArticleEntity(
            article_id=article.id,
            entity=e,
            entity_type="product"
        ))

    for row in batches:
        db.add(row)

    db.commit()