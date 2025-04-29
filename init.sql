-- Raw document table
CREATE TABLE IF NOT EXISTS db.documents (
    uuid BINARY(16) PRIMARY KEY NOT NULL, -- The Data type is chosen to make the the storage more space efficient
    title_en TEXT NOT NULL,
    title_source_language TEXT NOT NULL,
    body_en LONGTEXT NOT NULL,
    body_source_language LONGTEXT NOT NULL,
    summary_en MEDIUMTEXT NOT NULL,
    summary_source_language MEDIUMTEXT NOT NULL,
    publication_date VARCHAR(15) NOT NULL,
    url VARCHAR(100) NOT NULL,
    source VARCHAR(50) NOT NULL
);

-- Entity table
CREATE TABLE IF NOT EXISTS db.extracted_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid BINARY(16) NOT NULL,
    entity_type ENUM ('Person', 'Company', 'Location') NOT NULL,
    entity_text VARCHAR(100) NOT NULL,
    start_pos INT NOT NULL,
    end_pos INT NOT NULL,
    score DECIMAL(4, 2) NOT NULL CHECK (score BETWEEN 0 AND 1),
    is_matched BOOLEAN NOT NULL,
    matched_entity_id VARCHAR(100) DEFAULT NULL,
    matched_entity_name VARCHAR(100) DEFAULT NULL,
    updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Index for efficient lookup on these columns
    INDEX idx_uuid (uuid),
    INDEX idx_matched_entity_id (matched_entity_id),
    FOREIGN KEY (uuid) REFERENCES documents (uuid) ON DELETE CASCADE -- Link back to the document table using this column as a foreign key
) DEFAULT CHARSET = utf8mb4;

-- Reset the database to ensure a clean slate and bypass any InnoDB caching
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
