from fastapi.testclient import TestClient

import server
from server import ProgressPayload, SetProgress, status_rows


def test_status_rows_when_progress_has_completed_wrong_favorite_and_chopped_questions() -> None:
    payload = ProgressPayload(
        progress={
            "0": SetProgress(done=[0], wrong=[1], favorite=[2], excluded=[3], answers={"0": "A"}),
            "1": SetProgress(done=[4], favorite=[4], answers={"4": "AB"}),
        }
    )

    assert status_rows(payload) == [
        (1, "pdf-single", 1, True, False, False, False, "A"),
        (1, "pdf-single", 2, False, True, False, False, None),
        (1, "pdf-single", 3, False, False, True, False, None),
        (1, "pdf-single", 4, False, False, False, True, None),
        (1, "pdf-multi", 5, True, False, True, False, "AB"),
    ]


def test_progress_endpoints_when_storage_succeeds(monkeypatch) -> None:
    expected = {
        "0": {"done": [0], "wrong": [], "favorite": [], "excluded": [], "results": {"0": True}, "answers": {"0": "A"}},
        "1": {"done": [], "wrong": [], "favorite": [], "excluded": [], "results": {}, "answers": {}},
    }
    saved: list[ProgressPayload] = []

    monkeypatch.setattr(server, "load_progress", lambda: expected)
    monkeypatch.setattr(server, "replace_progress", lambda payload: saved.append(payload))
    client = TestClient(server.app)

    response = client.get("/api/progress")
    assert response.status_code == 200
    assert response.json() == expected

    update = {"progress": {"0": {"favorite": [0]}}}
    response = client.put("/api/progress", json=update)
    assert response.status_code == 204
    assert saved[0].progress["0"].favorite == [0]


def test_progress_export_endpoint_when_storage_succeeds(monkeypatch) -> None:
    expected = {
        "0": {"done": [0], "wrong": [], "favorite": [], "excluded": [], "results": {"0": True}, "answers": {"0": "A"}},
        "1": {"done": [], "wrong": [], "favorite": [], "excluded": [], "results": {}, "answers": {}},
    }
    monkeypatch.setattr(server, "load_progress", lambda: expected)
    client = TestClient(server.app)

    response = client.get("/api/progress/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "attachment" in response.headers["content-disposition"]
    body = response.json()
    assert body["schema_version"] == 1
    assert body["progress"] == expected
    assert body["exported_at"]


def test_progress_import_endpoint_when_payload_is_valid(monkeypatch) -> None:
    saved: list[ProgressPayload] = []
    expected = {
        "0": {"done": [2], "wrong": [], "favorite": [], "excluded": [], "results": {"2": True}, "answers": {"2": "B"}},
        "1": {"done": [], "wrong": [], "favorite": [], "excluded": [], "results": {}, "answers": {}},
    }
    monkeypatch.setattr(server, "quiz_catalog", lambda: [
        {"source_key": "pdf-single", "section": "single", "question_count": 896},
        {"source_key": "pdf-multi", "section": "multi", "question_count": 370},
    ])
    monkeypatch.setattr(server, "replace_progress", lambda payload: saved.append(payload))
    monkeypatch.setattr(server, "load_progress", lambda: expected)
    client = TestClient(server.app)

    response = client.post(
        "/api/progress/import",
        json={
            "schema_version": 1,
            "exported_at": "2026-09-03T00:00:00+00:00",
            "progress": {
                "0": {"done": [2], "answers": {"2": "B"}},
                "1": {},
            },
        },
    )

    assert response.status_code == 200
    assert saved[0].progress["0"].done == [2]
    assert response.json() == expected


def test_progress_import_endpoint_rejects_out_of_range_question(monkeypatch) -> None:
    monkeypatch.setattr(server, "quiz_catalog", lambda: [
        {"source_key": "pdf-single", "section": "single", "question_count": 2},
        {"source_key": "pdf-multi", "section": "multi", "question_count": 1},
    ])
    monkeypatch.setattr(server, "replace_progress", lambda payload: None)
    client = TestClient(server.app)

    response = client.post(
        "/api/progress/import",
        json={
            "schema_version": 1,
            "exported_at": "2026-09-03T00:00:00+00:00",
            "progress": {
                "0": {"done": [2]},
                "1": {},
            },
        },
    )

    assert response.status_code == 400


def test_quiz_endpoints_when_questions_are_served_from_database(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "quiz_catalog",
        lambda: [
            {"source_key": "pdf-single", "section": "single", "question_count": 896},
            {"source_key": "pdf-multi", "section": "multi", "question_count": 370},
        ],
    )
    monkeypatch.setattr(
        server,
        "read_quiz_question",
        lambda source_key, question_no: {
            "source_key": source_key,
            "question_no": question_no,
            "section": "single",
            "body": "题干",
            "options": [{"key": "A", "text": "选项 A"}],
        },
    )
    monkeypatch.setattr(
        server,
        "grade_quiz_question",
        lambda source_key, question_no, answer: {
            "is_correct": answer == "A",
            "correct_answer": "A",
        },
    )
    client = TestClient(server.app)

    catalog = client.get("/api/quiz/catalog")
    assert catalog.status_code == 200
    assert catalog.json() == {
        "sets": [
            {"source_key": "pdf-single", "section": "single", "question_count": 896},
            {"source_key": "pdf-multi", "section": "multi", "question_count": 370},
        ]
    }

    question = client.get("/api/quiz/questions/pdf-single/1")
    assert question.status_code == 200
    assert question.json() == {
        "source_key": "pdf-single",
        "question_no": 1,
        "section": "single",
        "body": "题干",
        "options": [{"key": "A", "text": "选项 A"}],
    }
    assert "correct_answer" not in question.json()

    result = client.post(
        "/api/quiz/questions/pdf-single/1/submit",
        json={"answer": "A"},
    )
    assert result.status_code == 200
    assert result.json() == {"is_correct": True, "correct_answer": "A"}
    assert client.get("/app-logic.js").status_code == 200
    assert client.get("/quiz-data.js").status_code == 404
