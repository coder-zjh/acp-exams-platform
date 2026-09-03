from fastapi.testclient import TestClient

import server
from server import ProgressPayload, SetProgress, status_rows


def test_status_rows_when_progress_has_completed_wrong_favorite_and_chopped_questions() -> None:
    payload = ProgressPayload(
        progress={
            "0": SetProgress(done=[0], wrong=[1], favorite=[2], excluded=[3]),
            "1": SetProgress(done=[4], favorite=[4]),
        }
    )

    assert status_rows(payload) == [
        (1, "pdf-single", 1, True, False, False, False),
        (1, "pdf-single", 2, False, True, False, False),
        (1, "pdf-single", 3, False, False, True, False),
        (1, "pdf-single", 4, False, False, False, True),
        (1, "pdf-multi", 5, True, False, True, False),
    ]


def test_progress_endpoints_when_storage_succeeds(monkeypatch) -> None:
    expected = {
        "0": {"done": [0], "wrong": [], "favorite": [], "excluded": [], "results": {"0": True}},
        "1": {"done": [], "wrong": [], "favorite": [], "excluded": [], "results": {}},
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
