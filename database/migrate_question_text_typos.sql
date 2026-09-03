UPDATE acp_questions
SET
  body = REPLACE(REPLACE(body, '接又', '接口'), '窗又', '窗口'),
  options_json = REPLACE(REPLACE(options_json, '接又', '接口'), '窗又', '窗口')
WHERE body LIKE '%接又%'
   OR body LIKE '%窗又%'
   OR options_json LIKE '%接又%'
   OR options_json LIKE '%窗又%';
