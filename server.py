from __future__ import annotations

import os
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, Literal

import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from pymysql.cursors import DictCursor
from typing_extensions import TypedDict

ROOT: Final = Path(__file__).parent
DEFAULT_USER_ID: Final = 1
SOURCE_KEYS: Final = ("pdf-single", "pdf-multi")
SourceKey = Literal["pdf-single", "pdf-multi"]
QuestionSection = Literal["single", "multi"]


class SetProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    done: list[int] = Field(default_factory=list)
    wrong: list[int] = Field(default_factory=list)
    favorite: list[int] = Field(default_factory=list)
    excluded: list[int] = Field(default_factory=list)
    results: dict[str, bool] = Field(default_factory=dict)
    answers: dict[str, str] = Field(default_factory=dict)


class ProgressPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    progress: dict[str, SetProgress]


class ProgressExportPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal[1]
    exported_at: datetime
    progress: dict[str, SetProgress]


class QuizCatalogEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_key: SourceKey
    section: QuestionSection
    question_count: int


class QuizCatalogResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    sets: list[QuizCatalogEntry]


class QuizOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    text: str


class QuizQuestionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_key: SourceKey
    question_no: int
    section: QuestionSection
    body: str
    options: list[QuizOption]


class QuizSubmission(BaseModel):
    model_config = ConfigDict(frozen=True)

    answer: str


class QuizGradeResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    is_correct: bool
    correct_answer: str


class BrowserSetProgress(TypedDict):
    done: list[int]
    wrong: list[int]
    favorite: list[int]
    excluded: list[int]
    results: dict[str, bool]
    answers: dict[str, str]


def db_config() -> dict[str, str | int]:
    return {
        "host": os.environ.get("ACA_DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("ACA_DB_PORT", "3306")),
        "user": os.environ.get("ACA_DB_USER", "root"),
        "password": os.environ.get("ACA_DB_PASSWORD", ""),
        "database": os.environ.get("ACA_DB_NAME", "acp_exams_platform"),
        "charset": "utf8mb4",
    }


@contextmanager
def connection() -> Iterator[pymysql.connections.Connection]:
    with pymysql.connect(**db_config(), cursorclass=DictCursor, autocommit=False) as conn:
        yield conn


def empty_progress() -> dict[str, BrowserSetProgress]:
    return {
        str(index): {"done": [], "wrong": [], "favorite": [], "excluded": [], "results": {}, "answers": {}}
        for index in range(len(SOURCE_KEYS))
    }


def load_progress() -> dict[str, BrowserSetProgress]:
    progress = empty_progress()
    sql = """
        SELECT q.source_key, q.question_no, s.is_completed, s.is_wrong,
               s.is_favorite, s.is_chopped, s.last_answer
        FROM acp_user_question_status AS s
        INNER JOIN acp_questions AS q ON q.id = s.question_id
        WHERE s.user_id = %s
    """
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(sql, (DEFAULT_USER_ID,))
        rows = cursor.fetchall()

    for row in rows:
        source_index = SOURCE_KEYS.index(str(row["source_key"]))
        set_progress = progress[str(source_index)]
        question_index = int(row["question_no"]) - 1
        if row["is_completed"]:
            set_progress["done"].append(question_index)
            set_progress["results"][str(question_index)] = not bool(row["is_wrong"])
        if row["is_wrong"]:
            set_progress["wrong"].append(question_index)
        if row["is_favorite"]:
            set_progress["favorite"].append(question_index)
        if row["is_chopped"]:
            set_progress["excluded"].append(question_index)
        if row["last_answer"]:
            set_progress["answers"][str(question_index)] = str(row["last_answer"])
    return progress


def status_rows(payload: ProgressPayload) -> list[tuple[int, str, int, bool, bool, bool, bool, str | None]]:
    rows: list[tuple[int, str, int, bool, bool, bool, bool, str | None]] = []
    for source_index, source_key in enumerate(SOURCE_KEYS):
        set_progress = payload.progress.get(str(source_index), SetProgress())
        indexes = set(set_progress.done) | set(set_progress.wrong) | set(set_progress.favorite) | set(set_progress.excluded)
        indexes |= {int(index) for index in set_progress.answers}
        for index in sorted(indexes):
            rows.append(
                (
                    DEFAULT_USER_ID,
                    source_key,
                    index + 1,
                    index in set_progress.done,
                    index in set_progress.wrong,
                    index in set_progress.favorite,
                    index in set_progress.excluded,
                    set_progress.answers.get(str(index)),
                )
            )
    return rows


def replace_progress(payload: ProgressPayload) -> None:
    insert = """
        INSERT INTO acp_user_question_status
          (user_id, question_id, is_completed, is_wrong, is_favorite, is_chopped, last_answer)
        SELECT %s, id, %s, %s, %s, %s, %s
        FROM acp_questions
        WHERE source_key = %s AND question_no = %s
    """
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute("DELETE FROM acp_user_question_status WHERE user_id = %s", (DEFAULT_USER_ID,))
        for user_id, source_key, question_no, completed, wrong, favorite, chopped, answer in status_rows(payload):
            cursor.execute(insert, (user_id, completed, wrong, favorite, chopped, answer, source_key, question_no))
        conn.commit()


def validate_import_progress(payload: ProgressExportPayload) -> None:
    expected_keys = {str(index) for index in range(len(SOURCE_KEYS))}
    if set(payload.progress) != expected_keys:
        raise HTTPException(status_code=400, detail="进度文件缺少有效题库数据")

    catalog = {str(index): int(entry["question_count"]) for index, entry in enumerate(quiz_catalog())}
    for set_index, set_progress in payload.progress.items():
        question_count = catalog.get(set_index)
        if question_count is None:
            raise HTTPException(status_code=400, detail="进度文件包含未知题库")
        for field_name in ("done", "wrong", "favorite", "excluded"):
            values = getattr(set_progress, field_name)
            if len(values) != len(set(values)) or any(value < 0 or value >= question_count for value in values):
                raise HTTPException(status_code=400, detail="进度文件包含无效题号")
        for mapping in (set_progress.results, set_progress.answers):
            for key in mapping:
                if not key.isdecimal() or str(int(key)) != key or int(key) < 0 or int(key) >= question_count:
                    raise HTTPException(status_code=400, detail="进度文件包含无效题号")


def quiz_catalog() -> list[dict[str, str | int]]:
    sql = """
        SELECT source_key, section, COUNT(*) AS question_count
        FROM acp_questions
        GROUP BY source_key, section
        ORDER BY FIELD(source_key, 'pdf-single', 'pdf-multi')
    """
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def read_quiz_question(source_key: SourceKey, question_no: int) -> dict[str, object]:
    sql = """
        SELECT source_key, question_no, section, body, options_json
        FROM acp_questions
        WHERE source_key = %s AND question_no = %s
    """
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(sql, (source_key, question_no))
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="题目不存在")
    options = json.loads(str(row["options_json"]))
    return {
        "source_key": row["source_key"],
        "question_no": row["question_no"],
        "section": row["section"],
        "body": row["body"],
        "options": [{"key": item["key"], "text": item["text"]} for item in options],
    }


def grade_quiz_question(
    source_key: SourceKey, question_no: int, answer: str
) -> dict[str, str | bool]:
    sql = """
        SELECT answer
        FROM acp_questions
        WHERE source_key = %s AND question_no = %s
    """
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(sql, (source_key, question_no))
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="题目不存在")
    correct_answer = str(row["answer"])
    return {
        "is_correct": "".join(sorted(answer.upper())) == "".join(sorted(correct_answer)),
        "correct_answer": correct_answer,
    }


app = FastAPI(title="ACP Exams Platform Progress API")


@app.get("/", response_class=FileResponse)
def get_index() -> FileResponse:
    return FileResponse(ROOT / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/app.js", response_class=FileResponse)
def get_app_script() -> FileResponse:
    return FileResponse(ROOT / "app.js", media_type="application/javascript", headers={"Cache-Control": "no-store"})


@app.get("/app-logic.js", response_class=FileResponse)
def get_app_logic_script() -> FileResponse:
    return FileResponse(ROOT / "app-logic.js", media_type="application/javascript", headers={"Cache-Control": "no-store"})


@app.get("/api/progress")
def get_progress() -> dict[str, BrowserSetProgress]:
    return load_progress()


@app.put("/api/progress", status_code=204)
def put_progress(payload: ProgressPayload) -> None:
    try:
        replace_progress(payload)
    except pymysql.MySQLError as error:
        raise HTTPException(status_code=500, detail="无法保存 MySQL 练习进度") from error


@app.get("/api/progress/export")
def export_progress() -> Response:
    payload = ProgressExportPayload(
        schema_version=1,
        exported_at=datetime.now(timezone.utc),
        progress=load_progress(),
    )
    content = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, indent=2)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="acp-progress.json"'},
    )


@app.post("/api/progress/import")
def import_progress(payload: ProgressExportPayload) -> dict[str, BrowserSetProgress]:
    validate_import_progress(payload)
    try:
        replace_progress(ProgressPayload(progress=payload.progress))
    except pymysql.MySQLError as error:
        raise HTTPException(status_code=500, detail="无法导入 MySQL 练习进度") from error
    return load_progress()


@app.get("/api/quiz/catalog", response_model=QuizCatalogResponse)
def get_quiz_catalog() -> QuizCatalogResponse:
    return QuizCatalogResponse(sets=quiz_catalog())


@app.get(
    "/api/quiz/questions/{source_key}/{question_no}",
    response_model=QuizQuestionResponse,
)
def get_quiz_question(
    source_key: SourceKey, question_no: int
) -> QuizQuestionResponse:
    return QuizQuestionResponse(**read_quiz_question(source_key, question_no))


@app.post(
    "/api/quiz/questions/{source_key}/{question_no}/submit",
    response_model=QuizGradeResponse,
)
def submit_quiz_question(
    source_key: SourceKey, question_no: int, submission: QuizSubmission
) -> QuizGradeResponse:
    return QuizGradeResponse(
        **grade_quiz_question(source_key, question_no, submission.answer)
    )
