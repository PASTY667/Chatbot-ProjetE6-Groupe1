-- ----------------------------------------------------------
-- Script MYSQL pour mcd 
-- ----------------------------------------------------------


-- ----------------------------
-- Table: user
-- ----------------------------
CREATE TABLE user (
  id_user INT NOT NULL AUTO_INCREMENT,
  id_LDAP VARCHAR(50) NOT NULL,
  admin TINYINT(1) NOT NULL,
  block TINYINT(1) NOT NULL,
  nbr_connexion INT NOT NULL,
  nbr_requete INT NOT NULL,
  nbr_doc_sent INT NOT NULL,
  CONSTRAINT user_PK PRIMARY KEY (id_user)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: session
-- ----------------------------
CREATE TABLE session (
  id_session INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  last_updated DATETIME NOT NULL,
  created_at DATETIME NOT NULL,
  id_user INT NOT NULL,
  CONSTRAINT session_PK PRIMARY KEY (id_session),
  CONSTRAINT session_id_user_FK FOREIGN KEY (id_user) REFERENCES user (id_user)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: logs
-- ----------------------------
CREATE TABLE logs (
  id_logs INT NOT NULL AUTO_INCREMENT,
  date DATETIME NOT NULL,
  ip_address VARCHAR(50) NOT NULL,
  id_user INT NOT NULL,
  CONSTRAINT logs_PK PRIMARY KEY (id_logs),
  CONSTRAINT logs_id_user_FK FOREIGN KEY (id_user) REFERENCES user (id_user)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: file
-- ----------------------------
CREATE TABLE file (
  id_fichier INT NOT NULL AUTO_INCREMENT,
  filename VARCHAR(100) NOT NULL,
  id_session INT NOT NULL,
  CONSTRAINT file_PK PRIMARY KEY (id_fichier),
  CONSTRAINT file_id_session_FK FOREIGN KEY (id_session) REFERENCES session (id_session)
)ENGINE=InnoDB;


-- ----------------------------
-- Table: message
-- ----------------------------
CREATE TABLE message (
  id_message INT NOT NULL AUTO_INCREMENT,
  content VARCHAR(4000) NOT NULL,
  date DATETIME NOT NULL,
  sender VARCHAR(50) NOT NULL,
  id_session INT NOT NULL,
  CONSTRAINT message_PK PRIMARY KEY (id_message),
  CONSTRAINT message_id_session_FK FOREIGN KEY (id_session) REFERENCES session (id_session)
)ENGINE=InnoDB;