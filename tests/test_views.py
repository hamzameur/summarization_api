from unittest.mock import patch

from summarization_api.views import app
from summarization_api.model import ApiExceptionName
from tests.common import (
    MOCK_TEXT_HANDLER,
    reset_mock_db,
    remove_mock_db_if_it_exists,
    HELLO_TEXT,
    HELLO_TEXT_ID,
)

MOCK_TEXT = (
    "Thomas A. Anderson is a man living two lives. By day he is an "
    "average computer programmer and by night a hacker known as "
    "Neo. Neo has always questioned his reality, but the truth is "
    "far beyond his imagination. Neo finds himself targeted by the "
    "police when he is contacted by Morpheus, a legendary computer "
    "hacker branded a terrorist by the government. Morpheus awakens "
    "Neo to the real world, a ravaged wasteland where most of "
    "humanity have been captured by a race of machines that live "
    "off of the humans' body heat and electrochemical energy and "
    "who imprison their minds within an artificial reality known as "
    "the Matrix. As a rebel against the machines, Neo must return to "
    "the Matrix and confront the agents: super-powerful computer "
    "programs devoted to snuffing out Neo and the entire human "
    "rebellion. "
)

MOCK_TEXT_ID: str = "76517f8d9b3710e89e12c87b24b93f52c27e74c8cce945f56df138be9c097ad4"


def test_store_text_and_get_id():
    reset_mock_db()
    with patch("summarization_api.views.TEXT_HANDLER", MOCK_TEXT_HANDLER):
        with app.test_client() as client:
            resp = client.post("/texts")
            assert resp.status_code == 400
            assert resp.json == {
                "code": 400,
                "name": ApiExceptionName.MISSING_REQUIRED_PARAMETER.value,
                "description": "text to store is missing",
            }

            resp = client.post("/texts", data={"text": MOCK_TEXT})
            assert resp.status_code == 200
            assert resp.json == {"textId": MOCK_TEXT_ID}
            # test idempotent behaviour
            assert client.post(
                "/texts", data={"text": MOCK_TEXT}
            ).json == {"textId": MOCK_TEXT_ID}

    remove_mock_db_if_it_exists()


def test_get_text_from_id():
    reset_mock_db()
    with patch("summarization_api.views.TEXT_HANDLER", MOCK_TEXT_HANDLER):
        with app.test_client() as client:
            resp = client.get(f"/texts/{MOCK_TEXT_ID}")
            assert resp.status_code == 404
            assert resp.json == {
                "code": 404,
                "name": ApiExceptionName.ID_NOT_FOUND.value,
                "description": f"No text stored under text id `{MOCK_TEXT_ID}`",
            }

            resp = client.post("/texts", data={"text": MOCK_TEXT})
            assert resp.status_code == 200
            assert resp.json == {"textId": MOCK_TEXT_ID}

            resp = client.get(f"/texts/{MOCK_TEXT_ID}")
            assert resp.status_code == 200
            assert resp.json == {"textId": MOCK_TEXT_ID, "text": MOCK_TEXT}

    remove_mock_db_if_it_exists()


def test_summarize_short_text():
    reset_mock_db()
    with patch("summarization_api.views.TEXT_HANDLER", MOCK_TEXT_HANDLER):
        with app.test_client() as client:
            resp = client.post("/texts", data={"text": HELLO_TEXT})
            assert resp.status_code == 200
            assert resp.json == {"textId": HELLO_TEXT_ID}

            resp = client.get(f"/texts/{HELLO_TEXT_ID}/summarize")
            assert resp.status_code == 501
            assert resp.json == {
                "code": 501,
                "name": ApiExceptionName.TEXT_TOO_SHORT.value,
                "description": "the current summarizer does not support text with"
                " less than two sentences",
            }

    remove_mock_db_if_it_exists()


def test_summarize_long_text():
    reset_mock_db()
    with patch("summarization_api.views.TEXT_HANDLER", MOCK_TEXT_HANDLER):
        with app.test_client() as client:
            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize")
            assert resp.status_code == 404
            assert resp.json == {
                "code": 404,
                "name": ApiExceptionName.ID_NOT_FOUND.value,
                "description": f"No text stored under text id `{MOCK_TEXT_ID}`",
            }

            resp = client.post("/texts", data={"text": MOCK_TEXT})
            assert resp.status_code == 200
            assert resp.json == {"textId": MOCK_TEXT_ID}

            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize")
            assert resp.status_code == 200
            assert resp.json == {
                "textId": MOCK_TEXT_ID,
                "summaryParameters": {"ratio": 0.2},
                "summary": "Morpheus awakens Neo to the real world,"
                " a ravaged wasteland where most of humanity"
                " have been captured by a race of machines"
                " that live off of the humans' body heat and electrochemical"
                " energy and who imprison their minds within an artificial"
                " reality known as the Matrix.",
            }

            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize?ratio=0.19")
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"ratio": 0.19}

            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize?ratio=0")
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"ratio": 0.20}

            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize?ratio=somethingweird")
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"ratio": 0.20}

            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize?wordCount=20")
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"wordCount": 20}

            resp = client.get(f"/texts/{MOCK_TEXT_ID}/summarize?wordCount=0")
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"wordCount": 10}

            resp = client.get(
                f"/texts/{MOCK_TEXT_ID}/summarize?wordCount=someweirdthing"
            )
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"wordCount": 10}

            resp = client.get(
                f"/texts/{MOCK_TEXT_ID}/summarize?wordCount=23&ratio=0.21"
            )
            assert resp.status_code == 200
            assert resp.json["summaryParameters"] == {"ratio": 0.21}

    remove_mock_db_if_it_exists()
