
-- Entity table
CREATE TABLE IF NOT EXISTS db.extracted_entities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  uuid BINARY(16) NOT NULL, -- The Data type is chosen to make the the storage more space efficient
  entity_type ENUM('Person', 'Company', 'Location') NOT NULL,
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
  INDEX idx_matched_entity_id (matched_entity_id)
) DEFAULT CHARSET = utf8mb4;

-- Raw document table
CREATE TABLE IF NOT EXISTS db.documents (
  id INT AUTO_INCREMENT PRIMARY KEY KEY,
  uuid VARCHAR(100) NOT NULL,
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
