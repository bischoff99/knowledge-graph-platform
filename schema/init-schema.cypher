// Knowledge Graph Platform - Initial Schema
// Property Graph Model for Neo4j
// Created: 2025-11-05

// ========================================
// CONSTRAINTS & INDEXES
// ========================================

// Project entities
CREATE CONSTRAINT project_name IF NOT EXISTS FOR (p:Project) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE INDEX project_status IF NOT EXISTS FOR (p:Project) ON (p.status);
CREATE INDEX project_criticality IF NOT EXISTS FOR (p:Project) ON (p.criticality);

// Configuration entities
CREATE CONSTRAINT config_name IF NOT EXISTS FOR (c:Configuration) REQUIRE c.name IS UNIQUE;
CREATE INDEX config_type IF NOT EXISTS FOR (c:Configuration) ON (c.config_type);

// Tool entities
CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE;
CREATE INDEX tool_status IF NOT EXISTS FOR (t:Tool) ON (t.status);

// Architecture/Pattern entities
CREATE CONSTRAINT pattern_name IF NOT EXISTS FOR (p:Pattern) REQUIRE p.name IS UNIQUE;
CREATE INDEX pattern_tags IF NOT EXISTS FOR (p:Pattern) ON (p.tags);

// Documentation/FAQ entities  
CREATE CONSTRAINT doc_name IF NOT EXISTS FOR (d:Documentation) REQUIRE d.name IS UNIQUE;
CREATE FULL TEXT INDEX faq_content IF NOT EXISTS FOR (d:Documentation) ON EACH [d.content, d.keywords];

// Temporal indexes
CREATE INDEX entity_last_updated IF NOT EXISTS FOR (e) ON (e.last_updated);
CREATE INDEX entity_created_at IF NOT EXISTS FOR (e) ON (e.created_at);

// Tag indexes (for hierarchical search)
CREATE INDEX entity_tags IF NOT EXISTS FOR (e) ON (e.tags);

// ========================================
// RELATIONSHIP TYPES (documented)
// ========================================

// Primary relationships:
// - IMPLEMENTS
// - OPTIMIZED_WITH  
// - EXPOSES
// - DEPENDS_ON_CRITICAL
// - IMPLEMENTS_PATTERN
// - APPLIES_PATTERN
// - REFERENCES
// - DOCUMENTED_IN
// - VALIDATED
// - CREATED
// - LEVERAGES
// - USES
// - PART_OF
// - COMPONENT_OF
// - SUPPORTS
// - STORED_IN
// - INCLUDES
// - ENFORCES_QUALITY_FOR

// All relationships support temporal properties:
// - valid_from (DateTime)
// - valid_to (DateTime, nullable)
// - observed_at (DateTime)
// - confidence (Float, 0.0-1.0)
// - provenance (String)
