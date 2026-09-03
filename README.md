# ACP Exams Platform

阿里云大模型 ACP 认证题库练习平台，题库来自网络。

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

## 支持项目

如果这个项目对你有帮助，可以通过以下方式支持维护：

| 微信支付 | 支付宝 |
| --- | --- |
| ![微信收款码](docs/payment/wechat.jpg) | ![支付宝收款码](docs/payment/alipay.jpg) |
