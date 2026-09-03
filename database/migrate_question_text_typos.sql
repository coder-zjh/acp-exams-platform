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
