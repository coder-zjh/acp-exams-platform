# 阿里云大模型 ACP 练习台

## MySQL 初始化

```bash
mysql -u root -p < schema.sql
mysql -u root -p aca_acp_exams < mysql-seed.sql
```

复制配置模板并填写 MySQL 密码：

```bash
cp .env.example .env
```

启动服务：

```bash
set -a
source .env
set +a
python3 -m uvicorn server:app --host 127.0.0.1 --port 8766
```

打开 `http://127.0.0.1:8766`。题目完成、错题、收藏和斩题状态会保存到 MySQL 的 `user_question_status` 表。
