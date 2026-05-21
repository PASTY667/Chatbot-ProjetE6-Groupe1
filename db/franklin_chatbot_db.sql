-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : jeu. 21 mai 2026 à 14:26
-- Version du serveur : 8.4.7
-- Version de PHP : 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `franklin_chatbot`
--

-- --------------------------------------------------------

--
-- Structure de la table `auth_session`
--

DROP TABLE IF EXISTS `auth_session`;
CREATE TABLE IF NOT EXISTS `auth_session` (
  `id_auth_session` bigint NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `session_uid` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_agent` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id_auth_session`),
  UNIQUE KEY `uk_auth_session_uid` (`session_uid`),
  KEY `idx_auth_session_user` (`id_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `demarrer`
--

DROP TABLE IF EXISTS `demarrer`;
CREATE TABLE IF NOT EXISTS `demarrer` (
  `id_user` int NOT NULL,
  `id_session` int NOT NULL,
  `id_message` int NOT NULL,
  PRIMARY KEY (`id_user`,`id_session`,`id_message`),
  KEY `demarrer_id_session_FK` (`id_session`),
  KEY `demarrer_id_message_FK` (`id_message`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `deposer`
--

DROP TABLE IF EXISTS `deposer`;
CREATE TABLE IF NOT EXISTS `deposer` (
  `id_file` int NOT NULL,
  `id_message` int NOT NULL,
  `id_user` int NOT NULL,
  PRIMARY KEY (`id_file`,`id_message`,`id_user`),
  KEY `deposer_id_message_FK` (`id_message`),
  KEY `deposer_id_user_FK` (`id_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `file`
--

DROP TABLE IF EXISTS `file`;
CREATE TABLE IF NOT EXISTS `file` (
  `id_file` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id_file`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `jwt_denylist`
--

DROP TABLE IF EXISTS `jwt_denylist`;
CREATE TABLE IF NOT EXISTS `jwt_denylist` (
  `id_deny` bigint NOT NULL AUTO_INCREMENT,
  `jti` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id_deny`),
  UNIQUE KEY `uk_jti` (`jti`),
  KEY `idx_jti_exp` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `log`
--

DROP TABLE IF EXISTS `log`;
CREATE TABLE IF NOT EXISTS `log` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state` tinyint(1) NOT NULL,
  `id_user` int NOT NULL,
  PRIMARY KEY (`id_log`),
  KEY `log_id_user_FK` (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `log`
--

INSERT INTO `log` (`id_log`, `date`, `ip_address`, `state`, `id_user`) VALUES
(1, '2026-05-21 08:31:14', '192.168.0.156', 1, 1);

-- --------------------------------------------------------

--
-- Structure de la table `message`
--

DROP TABLE IF EXISTS `message`;
CREATE TABLE IF NOT EXISTS `message` (
  `id_message` int NOT NULL AUTO_INCREMENT,
  `content` varchar(4000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` datetime NOT NULL,
  `sender` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_session` int NOT NULL,
  PRIMARY KEY (`id_message`),
  KEY `message_id_session_FK` (`id_session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `refresh_token`
--

DROP TABLE IF EXISTS `refresh_token`;
CREATE TABLE IF NOT EXISTS `refresh_token` (
  `id_refresh` bigint NOT NULL AUTO_INCREMENT,
  `id_auth_session` bigint NOT NULL,
  `token_hash` char(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked_at` datetime DEFAULT NULL,
  `replaced_by` bigint DEFAULT NULL,
  PRIMARY KEY (`id_refresh`),
  UNIQUE KEY `uk_refresh_hash` (`token_hash`),
  KEY `idx_refresh_session` (`id_auth_session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `session`
--

DROP TABLE IF EXISTS `session`;
CREATE TABLE IF NOT EXISTS `session` (
  `id_session` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_updated` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id_session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id_user` int NOT NULL AUTO_INCREMENT,
  `id_LDAP` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `nbr_connexion` int NOT NULL,
  `nbr_requete` int NOT NULL,
  `nbr_doc_sent` int NOT NULL,
  PRIMARY KEY (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `user`
--

INSERT INTO `user` (`id_user`, `id_LDAP`, `admin`, `enabled`, `nbr_connexion`, `nbr_requete`, `nbr_doc_sent`) VALUES
(1, '1', 1, 1, 15, 15, 15),
(2, '2', 0, 1, 17, 19, 18),
(3, '3', 1, 1, 14, 14, 14);

-- --------------------------------------------------------

--
-- Structure de la table `vector_document`
--

DROP TABLE IF EXISTS `vector_document`;
CREATE TABLE IF NOT EXISTS `vector_document` (
  `id_vector_doc` bigint NOT NULL AUTO_INCREMENT,
  `id_file` int NOT NULL,
  `id_user` int NOT NULL,
  `id_session` int DEFAULT NULL,
  `scope` enum('company','user_session') COLLATE utf8mb4_unicode_ci NOT NULL,
  `collection_name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `doc_id` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `chroma_ids_count` int NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL,
  `expires_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id_vector_doc`),
  KEY `idx_vector_scope` (`scope`),
  KEY `idx_vector_session` (`id_session`),
  KEY `idx_vector_user` (`id_user`),
  KEY `idx_vector_collection_doc` (`collection_name`,`doc_id`),
  KEY `fk_vector_file` (`id_file`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `auth_session`
--
ALTER TABLE `auth_session`
  ADD CONSTRAINT `fk_auth_session_user` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`);

--
-- Contraintes pour la table `demarrer`
--
ALTER TABLE `demarrer`
  ADD CONSTRAINT `demarrer_id_message_FK` FOREIGN KEY (`id_message`) REFERENCES `message` (`id_message`),
  ADD CONSTRAINT `demarrer_id_session_FK` FOREIGN KEY (`id_session`) REFERENCES `session` (`id_session`),
  ADD CONSTRAINT `demarrer_id_user_FK` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`);

--
-- Contraintes pour la table `deposer`
--
ALTER TABLE `deposer`
  ADD CONSTRAINT `deposer_id_file_FK` FOREIGN KEY (`id_file`) REFERENCES `file` (`id_file`),
  ADD CONSTRAINT `deposer_id_message_FK` FOREIGN KEY (`id_message`) REFERENCES `message` (`id_message`),
  ADD CONSTRAINT `deposer_id_user_FK` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`);

--
-- Contraintes pour la table `log`
--
ALTER TABLE `log`
  ADD CONSTRAINT `log_id_user_FK` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`);

--
-- Contraintes pour la table `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `message_id_session_FK` FOREIGN KEY (`id_session`) REFERENCES `session` (`id_session`);

--
-- Contraintes pour la table `refresh_token`
--
ALTER TABLE `refresh_token`
  ADD CONSTRAINT `fk_refresh_session` FOREIGN KEY (`id_auth_session`) REFERENCES `auth_session` (`id_auth_session`);

--
-- Contraintes pour la table `vector_document`
--
ALTER TABLE `vector_document`
  ADD CONSTRAINT `fk_vector_file` FOREIGN KEY (`id_file`) REFERENCES `file` (`id_file`),
  ADD CONSTRAINT `fk_vector_session` FOREIGN KEY (`id_session`) REFERENCES `session` (`id_session`),
  ADD CONSTRAINT `fk_vector_user` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
