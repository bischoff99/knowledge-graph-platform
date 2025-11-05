"""
LLM-driven Entity and Relation Extraction
Combines spaCy NER with LLM fallback for knowledge graph population
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

import spacy
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Triple(Dict):
    """Entity-Relation-Entity triple with metadata"""
    def __init__(self, subject: str, predicate: str, object: str, 
                 confidence: float = 1.0, source: str = "", provenance: dict = None):
        super().__init__()
        self['subject'] = subject
        self['predicate'] = predicate
        self['object'] = object
        self['confidence'] = confidence
        self['source'] = source
        self['provenance'] = provenance or {}
        self['extracted_at'] = datetime.now().isoformat()


class LLMExtractor:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str,
                 spacy_model: str = "en_core_web_sm"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Load spaCy model
        try:
            self.nlp = spacy.load(spacy_model)
            logger.info(f"Loaded spaCy model: {spacy_model}")
        except OSError:
            logger.warning(f"spaCy model {spacy_model} not found. Run: python -m spacy download {spacy_model}")
            self.nlp = None
    
    def close(self):
        self.driver.close()
    
    def extract_entities_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'name': ent.text,
                'type': ent.label_,
                'confidence': 0.85,  # spaCy baseline
                'method': 'spacy',
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def extract_relations_patterns(self, text: str) -> List[Triple]:
        """Extract relations using dependency parsing"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        triples = []
        
        # Simple subject-verb-object patterns
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                # Find subject
                subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubjpass")]
                # Find object
                objects = [child for child in token.children if child.dep_ in ("dobj", "attr", "oprd")]
                
                for subj in subjects:
                    for obj in objects:
                        triples.append(Triple(
                            subject=subj.text,
                            predicate=token.lemma_,
                            object=obj.text,
                            confidence=0.7,
                            source="spacy_dep_parse"
                        ))
        
        return triples
    
    def extract_with_llm_fallback(self, text: str, use_llm: bool = False) -> Tuple[List[Dict], List[Triple]]:
        """
        Extract entities and relations with optional LLM fallback
        
        Strategy:
        1. Use spaCy for initial extraction (fast, local)
        2. If use_llm=True and confidence < threshold, call LLM for verification
        3. Combine results with provenance tracking
        """
        # spaCy extraction
        entities = self.extract_entities_spacy(text)
        relations = self.extract_relations_patterns(text)
        
        # LLM fallback (placeholder - integrate with OpenAI/local LLM)
        if use_llm and len(entities) < 3:
            logger.info("Low entity count, LLM fallback would trigger here")
            # TODO: Implement LLM extraction
            # - Use few-shot prompting with examples
            # - Parse JSON response with (entity, type, confidence)
            # - Merge with spaCy results (higher confidence wins)
        
        return entities, relations
    
    def upsert_triple(self, triple: Triple, batch: bool = False) -> None:
        """Insert triple into Neo4j with provenance"""
        cypher = """
        MERGE (s:Entity {name: $subject})
        ON CREATE SET s.created_at = datetime(), s.source = $source
        
        MERGE (o:Entity {name: $object})
        ON CREATE SET o.created_at = datetime(), o.source = $source
        
        MERGE (s)-[r:EXTRACTED_RELATION {type: $predicate}]->(o)
        ON CREATE SET 
            r.confidence = $confidence,
            r.extracted_at = datetime($extracted_at),
            r.source = $source,
            r.provenance = $provenance
        ON MATCH SET
            r.last_seen = datetime($extracted_at),
            r.observation_count = coalesce(r.observation_count, 0) + 1
        """
        
        with self.driver.session() as session:
            session.run(cypher, 
                subject=triple['subject'],
                predicate=triple['predicate'],
                object=triple['object'],
                confidence=triple['confidence'],
                extracted_at=triple['extracted_at'],
                source=triple['source'],
                provenance=triple['provenance']
            )
    
    def upsert_triples_batch(self, triples: List[Triple]) -> int:
        """Batch upsert triples for performance"""
        cypher = """
        UNWIND $triples AS t
        
        MERGE (s:Entity {name: t.subject})
        ON CREATE SET s.created_at = datetime(), s.source = t.source
        
        MERGE (o:Entity {name: t.object})
        ON CREATE SET o.created_at = datetime(), o.source = t.source
        
        MERGE (s)-[r:EXTRACTED_RELATION {type: t.predicate}]->(o)
        ON CREATE SET 
            r.confidence = t.confidence,
            r.extracted_at = datetime(t.extracted_at),
            r.source = t.source
        ON MATCH SET
            r.last_seen = datetime(t.extracted_at),
            r.observation_count = coalesce(r.observation_count, 0) + 1
        
        RETURN count(r) AS relations_created
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, triples=[dict(t) for t in triples])
            return result.single()["relations_created"]
    
    def process_document(self, text: str, doc_id: str, use_llm: bool = False) -> Dict[str, Any]:
        """Process document and extract knowledge"""
        logger.info(f"Processing document: {doc_id}")
        
        # Extract
        entities, relations = self.extract_with_llm_fallback(text, use_llm=use_llm)
        
        # Upsert
        if relations:
            count = self.upsert_triples_batch(relations)
            logger.info(f"Upserted {count} relations from {doc_id}")
        
        return {
            "document_id": doc_id,
            "entities_extracted": len(entities),
            "relations_extracted": len(relations),
            "method": "spacy" + (" + llm" if use_llm else "")
        }


if __name__ == '__main__':
    # Example usage
    extractor = LLMExtractor(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test1234"
    )
    
    sample_text = """
    The EasyPost MCP Project depends on Desktop Commander MCP for file operations.
    The project uses FastAPI and achieves 97.3% test pass rate.
    It implements the M3 Max Parallel Processing Pattern with 32 workers.
    """
    
    result = extractor.process_document(sample_text, "sample-doc-001")
    print(f"Extracted {result['relations_extracted']} relations")
    
    extractor.close()
