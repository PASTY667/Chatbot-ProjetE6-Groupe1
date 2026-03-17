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