CREATE TABLE IF NOT EXISTS db.extracted_entities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  uuid BINARY(16) NOT NULL,
  entity_type ENUM('Person', 'Company', 'Location') NOT NULL,
  entity_text VARCHAR(100) NOT NULL,
  start_pos INT NOT NULL,
  end_pos INT NOT NULL,
  is_matched BOOLEAN NOT NULL,
  matched_entity_id VARCHAR(100) DEFAULT NULL,
  matched_entity_name VARCHAR(100) DEFAULT NULL,
  updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  -- Index for efficient lookup on these columns
  INDEX idx_uuid (uuid),
  INDEX idx_matched_entity_id (matched_entity_id)
) DEFAULT CHARSET = utf8mb4;
