UPDATE acp_questions
SET
  body = REPLACE(REPLACE(body, '接又', '接口'), '窗又', '窗口'),
  options_json = REPLACE(REPLACE(options_json, '接又', '接口'), '窗又', '窗口')
WHERE body LIKE '%接又%'
   OR body LIKE '%窗又%'
   OR options_json LIKE '%接又%'
   OR options_json LIKE '%窗又%';

UPDATE acp_questions
SET
  body = REPLACE(REPLACE(body, '又 语', '口语'), '又语', '口语'),
  options_json = REPLACE(REPLACE(options_json, '又 语', '口语'), '又语', '口语')
WHERE body LIKE '%又 语%'
   OR body LIKE '%又语%'
   OR options_json LIKE '%又 语%'
   OR options_json LIKE '%又语%';

UPDATE acp_questions
SET
  body = REPLACE(body, '端又', '端口'),
  options_json = REPLACE(options_json, '端又', '端口')
WHERE body LIKE '%端又%'
   OR options_json LIKE '%端又%';

UPDATE acp_questions
SET
  body = REPLACE(body, '又头', '口头'),
  options_json = REPLACE(options_json, '又头', '口头')
WHERE body LIKE '%又头%'
   OR options_json LIKE '%又头%';

UPDATE acp_questions
SET
  body = REPLACE(body, '又吻', '口吻'),
  options_json = REPLACE(options_json, '又吻', '口吻')
WHERE source_key = 'pdf-multi' AND question_no = 205;

UPDATE acp_questions
SET
  body = REPLACE(body, '忌又', '忌口'),
  options_json = REPLACE(options_json, '忌又', '忌口')
WHERE source_key = 'pdf-single' AND question_no IN (574, 659);

UPDATE acp_questions
SET
  body = REPLACE(REPLACE(body, '一又10', '一口10'), '这又井', '这口井'),
  options_json = REPLACE(REPLACE(options_json, '一又10', '一口10'), '这又井', '这口井')
WHERE source_key = 'pdf-single' AND question_no = 585;

UPDATE acp_questions
SET
  body = REPLACE(body, '出又', '出口'),
  options_json = REPLACE(options_json, '出又', '出口')
WHERE source_key = 'pdf-single' AND question_no IN (643, 736);

UPDATE acp_questions
SET
  body = REPLACE(body, '又号', '口号'),
  options_json = REPLACE(options_json, '又号', '口号')
WHERE source_key = 'pdf-single' AND question_no = 718;

UPDATE acp_questions
SET
  body = REPLACE(body, '又吻', '口吻'),
  options_json = REPLACE(options_json, '又吻', '口吻')
WHERE source_key = 'pdf-single' AND question_no = 757;

UPDATE acp_questions
SET
  body = REPLACE(body, '人又统计', '人口统计'),
  options_json = REPLACE(options_json, '人又统计', '人口统计')
WHERE source_key = 'pdf-single' AND question_no = 762;
