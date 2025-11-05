// Migration 001: Initial Schema Setup
// Created: 2025-11-05
// Description: Create base constraints and indexes

// Constraints
CREATE CONSTRAINT project_name IF NOT EXISTS FOR (p:Project) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;

// Indexes
CREATE INDEX project_status IF NOT EXISTS FOR (p:Project) ON (p.status);
CREATE INDEX entity_tags IF NOT EXISTS FOR (e) ON (e.tags);

// Verification
SHOW CONSTRAINTS;
SHOW INDEXES;
