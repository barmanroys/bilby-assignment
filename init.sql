-- Select the same name as the database for the schema
CREATE SCHEMA db;

-- Raw document table
CREATE TABLE IF NOT EXISTS db.documents (
    uuid BYTEA PRIMARY KEY NOT NULL CHECK (LENGTH (uuid) = 16),
    title_en TEXT NOT NULL,
    title_source_language TEXT NOT NULL,
    body_en TEXT NOT NULL,
    body_source_language TEXT NOT NULL,
    summary_en TEXT NOT NULL,
    summary_source_language TEXT NOT NULL,
    publication_date VARCHAR(15) NOT NULL,
    url VARCHAR(100) NOT NULL,
    source VARCHAR(50) NOT NULL
);

-- Entity table
CREATE TABLE IF NOT EXISTS db.extracted_entities (
    id SERIAL PRIMARY KEY, -- Use SERIAL for auto-incrementing IDs
    uuid BYTEA NOT NULL CHECK (LENGTH (uuid) = 16),
    entity_type VARCHAR(8) NOT NULL CHECK (entity_type IN ('Person', 'Company', 'Location')), -- Pgsql lacks enum
    entity_text VARCHAR(100) NOT NULL,
    start_pos INT NOT NULL,
    end_pos INT NOT NULL,
    score DECIMAL(4, 2) NOT NULL CHECK (score BETWEEN 0 AND 1),
    is_matched BOOLEAN NOT NULL,
    matched_entity_id VARCHAR(100) DEFAULT NULL,
    matched_entity_name VARCHAR(100) DEFAULT NULL,
    updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uuid) REFERENCES db.documents (uuid) ON DELETE CASCADE -- Link back to the document table
);

-- PGSQL lacks inline index creation
CREATE INDEX idx_uuid ON db.extracted_entities (uuid);

CREATE INDEX idx_matched_entity_id ON db.extracted_entities (matched_entity_id);

-- Reset the database to ensure a clean slate and bypass any storage caching
DELETE FROM db.documents
WHERE
    true;

DELETE FROM db.extracted_entities
WHERE
    true;

-- Create the view for user's convenience
CREATE
OR REPLACE VIEW db.extracted_entities_documents AS
SELECT
    d.title_en,
    d.title_source_language,
    d.body_en,
    d.body_source_language,
    d.summary_en,
    d.summary_source_language,
    d.publication_date,
    d.url,
    d.source,
    e.*
FROM
    db.extracted_entities AS e
    INNER JOIN db.documents AS d ON e.uuid = d.uuid;
