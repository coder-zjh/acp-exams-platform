CREATE DATABASE IF NOT EXISTS acp_exams_platform
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE acp_exams_platform;

CREATE TABLE IF NOT EXISTS acp_users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS acp_questions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source_key VARCHAR(64) NOT NULL,
  question_no INT NOT NULL,
  section ENUM('single', 'multi') NOT NULL,
  body TEXT NOT NULL,
  options_json JSON NOT NULL,
  answer VARCHAR(16) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_questions_source_no (source_key, question_no),
  KEY idx_questions_section (section)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS acp_user_question_status (
  user_id BIGINT UNSIGNED NOT NULL,
  question_id BIGINT UNSIGNED NOT NULL,
  is_completed TINYINT(1) NOT NULL DEFAULT 0,
  is_wrong TINYINT(1) NOT NULL DEFAULT 0,
  is_favorite TINYINT(1) NOT NULL DEFAULT 0,
  is_chopped TINYINT(1) NOT NULL DEFAULT 0,
  last_answer VARCHAR(16) NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, question_id),
  CONSTRAINT fk_status_user FOREIGN KEY (user_id) REFERENCES acp_users(id) ON DELETE CASCADE,
  CONSTRAINT fk_status_question FOREIGN KEY (question_id) REFERENCES acp_questions(id) ON DELETE CASCADE,
  KEY idx_status_wrong (user_id, is_wrong),
  KEY idx_status_favorite (user_id, is_favorite),
  KEY idx_status_chopped (user_id, is_chopped),
  KEY idx_status_completed (user_id, is_completed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS acp_study_activity (
  user_id BIGINT UNSIGNED NOT NULL,
  activity_date DATE NOT NULL,
  completed_count INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, activity_date),
  CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES acp_users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO acp_users (id, username)
VALUES (1, 'default')
ON DUPLICATE KEY UPDATE username = VALUES(username);
