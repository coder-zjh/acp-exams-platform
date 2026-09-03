from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final

import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from pymysql.cursors import DictCursor
from typing_extensions import TypedDict

ROOT: Final = Path(__file__).parent
DEFAULT_USER_ID: Final = 1
SOURCE_KEYS: Final = ("pdf-single", "pdf-multi")


class SetProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    done: list[int] = Field(default_factory=list)
    wrong: list[int] = Field(default_factory=list)
    favorite: list[int] = Field(default_factory=list)
    excluded: list[int] = Field(default_factory=list)
    results: dict[str, bool] = Field(default_factory=dict)


class ProgressPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    progress: dict[str, SetProgress]


class BrowserSetProgress(TypedDict):
    done: list[int]
    wrong: list[int]
    favorite: list[int]
    excluded: list[int]
    results: dict[str, bool]


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
        str(index): {"done": [], "wrong": [], "favorite": [], "excluded": [], "results": {}}
        for index in range(len(SOURCE_KEYS))
    }


def load_progress() -> dict[str, BrowserSetProgress]:
    progress = empty_progress()
    sql = """
        SELECT q.source_key, q.question_no, s.is_completed, s.is_wrong,
               s.is_favorite, s.is_chopped
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
    return progress


def status_rows(payload: ProgressPayload) -> list[tuple[int, str, int, bool, bool, bool, bool]]:
    rows: list[tuple[int, str, int, bool, bool, bool, bool]] = []
    for source_index, source_key in enumerate(SOURCE_KEYS):
        set_progress = payload.progress.get(str(source_index), SetProgress())
        indexes = set(set_progress.done) | set(set_progress.wrong) | set(set_progress.favorite) | set(set_progress.excluded)
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
                )
            )
    return rows


def replace_progress(payload: ProgressPayload) -> None:
    insert = """
        INSERT INTO acp_user_question_status
          (user_id, question_id, is_completed, is_wrong, is_favorite, is_chopped)
        SELECT %s, id, %s, %s, %s, %s
        FROM acp_questions
        WHERE source_key = %s AND question_no = %s
    """
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute("DELETE FROM acp_user_question_status WHERE user_id = %s", (DEFAULT_USER_ID,))
        for user_id, source_key, question_no, completed, wrong, favorite, chopped in status_rows(payload):
            cursor.execute(insert, (user_id, completed, wrong, favorite, chopped, source_key, question_no))
        conn.commit()


app = FastAPI(title="ACP Exams Platform Progress API")


@app.get("/api/progress")
def get_progress() -> dict[str, BrowserSetProgress]:
    return load_progress()


@app.put("/api/progress", status_code=204)
def put_progress(payload: ProgressPayload) -> None:
    try:
        replace_progress(payload)
    except pymysql.MySQLError as error:
        raise HTTPException(status_code=500, detail="无法保存 MySQL 练习进度") from error


app.mount("/", StaticFiles(directory=ROOT, html=True), name="web")
