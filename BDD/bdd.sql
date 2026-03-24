-- ----------------------------------------------------------
-- Script MYSQL pour mcd 
-- ----------------------------------------------------------


-- ----------------------------
-- Table: file
-- ----------------------------
CREATE TABLE file (
  id_file INT NOT NULL,
  filename VARCHAR(100) NOT NULL,
  CONSTRAINT file_PK PRIMARY KEY (id_file)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: session
-- ----------------------------
CREATE TABLE session (
  id_session INT NOT NULL,
  name VARCHAR(50) NOT NULL,
  last_updated DATETIME NOT NULL,
  created_at DATETIME NOT NULL,
  CONSTRAINT session_PK PRIMARY KEY (id_session)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: user
-- ----------------------------
CREATE TABLE user (
  id_user INT NOT NULL,
  id_LDAP VARCHAR(50) NOT NULL,
  admin TINYINT(1) NOT NULL,
  enabled TINYINT(1) NOT NULL,
  nbr_connexion INT NOT NULL,
  nbr_requete INT NOT NULL,
  nbr_doc_sent INT NOT NULL,
  CONSTRAINT user_PK PRIMARY KEY (id_user)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: log
-- ----------------------------
CREATE TABLE log (
  id_log INT NOT NULL,
  date DATETIME NOT NULL,
  ip_address VARCHAR(50) NOT NULL,
  state TINYINT(1) NOT NULL,
  id_user INT NOT NULL,
  CONSTRAINT log_PK PRIMARY KEY (id_log),
  CONSTRAINT log_id_user_FK FOREIGN KEY (id_user) REFERENCES user (id_user)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: message
-- ----------------------------
CREATE TABLE message (
  id_message INT NOT NULL,
  content VARCHAR(4000) NOT NULL,
  date DATETIME NOT NULL,
  sender VARCHAR(50) NOT NULL,
  id_session INT NOT NULL,
  CONSTRAINT message_PK PRIMARY KEY (id_message),
  CONSTRAINT message_id_session_FK FOREIGN KEY (id_session) REFERENCES session (id_session)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: demarrer
-- ----------------------------
CREATE TABLE demarrer (
  id_user INT NOT NULL,
  id_session INT NOT NULL,
  id_message INT NOT NULL,
  CONSTRAINT demarrer_PK PRIMARY KEY (id_user, id_session, id_message),
  CONSTRAINT demarrer_id_user_FK FOREIGN KEY (id_user) REFERENCES user (id_user),
  CONSTRAINT demarrer_id_session_FK FOREIGN KEY (id_session) REFERENCES session (id_session),
  CONSTRAINT demarrer_id_message_FK FOREIGN KEY (id_message) REFERENCES message (id_message)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: deposer
-- ----------------------------
CREATE TABLE deposer (
  id_file INT NOT NULL,
  id_message INT NOT NULL,
  id_user INT NOT NULL,
  CONSTRAINT deposer_PK PRIMARY KEY (id_file, id_message, id_user),
  CONSTRAINT deposer_id_file_FK FOREIGN KEY (id_file) REFERENCES file (id_file),
  CONSTRAINT deposer_id_message_FK FOREIGN KEY (id_message) REFERENCES message (id_message),
  CONSTRAINT deposer_id_user_FK FOREIGN KEY (id_user) REFERENCES user (id_user)
)ENGINE=InnoDB;

-- ----------------------------
-- Table: vector_document
-- ----------------------------
CREATE TABLE vector_document (
  id_vector_doc BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_file INT NOT NULL,
  id_user INT NOT NULL,
  id_session INT NULL,                    -- null si doc globale admin
  scope ENUM('company','user_session') NOT NULL,
  collection_name VARCHAR(120) NOT NULL,
  doc_id VARCHAR(120) NOT NULL,
  chroma_ids_count INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL,
  expires_at DATETIME NULL,               -- TTL pour docs user/session
  deleted_at DATETIME NULL,
  KEY idx_vector_scope (scope),
  KEY idx_vector_session (id_session),
  KEY idx_vector_user (id_user),
  KEY idx_vector_collection_doc (collection_name, doc_id),
  CONSTRAINT fk_vector_file FOREIGN KEY (id_file) REFERENCES file(id_file),
  CONSTRAINT fk_vector_user FOREIGN KEY (id_user) REFERENCES user(id_user),
  CONSTRAINT fk_vector_session FOREIGN KEY (id_session) REFERENCES session(id_session)
) ENGINE=InnoDB;

-- ----------------------------
-- Table: jwt_denylist
-- ----------------------------
CREATE TABLE jwt_denylist (
  id_deny BIGINT AUTO_INCREMENT PRIMARY KEY,
  jti CHAR(36) NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL,
  UNIQUE KEY uk_jti (jti),
  KEY idx_jti_exp (expires_at)
) ENGINE=InnoDB;

-- ----------------------------
-- Table: refresh_token
-- ----------------------------
CREATE TABLE refresh_token (
  id_refresh BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_auth_session BIGINT NOT NULL,
  token_hash CHAR(64) NOT NULL,           -- SHA-256 du refresh token
  created_at DATETIME NOT NULL,
  expires_at DATETIME NOT NULL,
  revoked_at DATETIME NULL,
  replaced_by BIGINT NULL,
  UNIQUE KEY uk_refresh_hash (token_hash),
  KEY idx_refresh_session (id_auth_session),
  CONSTRAINT fk_refresh_session FOREIGN KEY (id_auth_session) REFERENCES auth_session(id_auth_session)
) ENGINE=InnoDB;

-- ----------------------------
-- Table: auth_token
-- ----------------------------
CREATE TABLE auth_session (
  id_auth_session BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_user INT NOT NULL,
  session_uid CHAR(36) NOT NULL,          -- UUID côté API
  user_agent VARCHAR(255) NULL,
  ip_address VARCHAR(50) NULL,
  created_at DATETIME NOT NULL,
  expires_at DATETIME NOT NULL,
  revoked_at DATETIME NULL,
  UNIQUE KEY uk_auth_session_uid (session_uid),
  KEY idx_auth_session_user (id_user),
  CONSTRAINT fk_auth_session_user FOREIGN KEY (id_user) REFERENCES user(id_user)
) ENGINE=InnoDB;