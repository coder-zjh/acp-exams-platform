CREATE DATABASE IF NOT EXISTS acp_exams_platform
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

RENAME TABLE
  aca_acp_exams.users TO acp_exams_platform.acp_users,
  aca_acp_exams.questions TO acp_exams_platform.acp_questions,
  aca_acp_exams.user_question_status TO acp_exams_platform.acp_user_question_status,
  aca_acp_exams.study_activity TO acp_exams_platform.acp_study_activity;
