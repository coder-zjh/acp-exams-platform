# ACP Exams Platform

阿里云大模型 ACP 认证题库练习平台，题库来自桌面 PDF，已去重。

## 获取项目

```bash
git clone git@github.com:coder-zjh/acp-exams-platform.git
cd acp-exams-platform
```

## MySQL 初始化

```bash
mysql -u root -p < schema.sql
mysql -u root -p acp_exams_platform < mysql-seed.sql
```

复制配置模板并填写 MySQL 密码：

```bash
cp .env.example .env
```

编辑 `.env`，填写 `ACA_DB_PASSWORD`。`.env` 已被 Git 忽略，不会上传到 GitHub。

启动服务：

```bash
set -a
source .env
set +a
python3 -m uvicorn server:app --host 127.0.0.1 --port 8765
```

打开 `http://127.0.0.1:8765`。题目完成、错题、收藏和斩题状态会保存到 MySQL 的 `acp_user_question_status` 表。

## 依赖

```bash
python3 -m pip install fastapi uvicorn pymysql pydantic typing-extensions
```
