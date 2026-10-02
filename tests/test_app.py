from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app, follow_redirects=False) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"] == app_module.activities["Chess Club"]


def test_signup_adds_participant_and_returns_confirmation(client):
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_without_changing_participants(client):
    participants_before = app_module.activities["Chess Club"]["participants"].copy()

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": participants_before[0]},
    )

    assert response.status_code == 400
    assert app_module.activities["Chess Club"]["participants"] == participants_before


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_root_redirects_to_static_index(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"