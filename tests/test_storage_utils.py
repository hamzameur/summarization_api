import sqlite3
from datetime import datetime
from pathlib import Path
from sqlite3 import IntegrityError
from unittest.mock import patch

import pytest


from summarization_api.model import TextIdNotFoundError, TooManyTextsDbError
from summarization_api.storage_utils import (
    TABLE_TEXTS,
    get_text_hash,
)
from tests.common import (
    reset_mock_db,
    remove_mock_db_if_it_exists,
    MOCK_DB_NAME,
    MOCK_TEXT_HANDLER,
    HELLO_TEXT,
    HELLO_TEXT_ID,
)


def test_init_db():
    reset_mock_db()
    db_path = Path(MOCK_DB_NAME)
    assert db_path.is_file()
    remove_mock_db_if_it_exists()


def test_get_text_hash():
    assert get_text_hash(text=HELLO_TEXT) == HELLO_TEXT_ID


def test_insert_text_and_id():
    reset_mock_db()

    assert len(MOCK_TEXT_HANDLER._retrieve_text_by_id(text_id=HELLO_TEXT_ID)) == 0
    MOCK_TEXT_HANDLER._insert_text_and_id(text=HELLO_TEXT, text_id=HELLO_TEXT_ID)
    res = get_all_rows()
    assert len(res) == 1
    first_row = res[0]
    assert first_row[0] == HELLO_TEXT_ID
    assert first_row[2] == HELLO_TEXT

    with pytest.raises(IntegrityError):
        with sqlite3.connect(MOCK_DB_NAME) as con:
            cur = con.cursor()
            cur.execute(
                f"insert into {TABLE_TEXTS} (TEXT_ID, TEXT)"
                f" VALUES ('{HELLO_TEXT_ID}', 'some text')"
            )
            con.commit()
    res = get_all_rows()
    assert len(res) == 1
    assert first_row == res[0]
    remove_mock_db_if_it_exists()


def get_all_rows():
    with sqlite3.connect(MOCK_DB_NAME) as con:
        cur = con.cursor()
        res = cur.execute(f"select * from {TABLE_TEXTS}").fetchall()
    return res


def test_retrieve_text_by_id():
    reset_mock_db()
    assert MOCK_TEXT_HANDLER._retrieve_text_by_id(text_id="a") == []
    with sqlite3.connect(MOCK_DB_NAME) as con:
        cur = con.cursor()
        cur.execute(f"insert into {TABLE_TEXTS} (TEXT_ID, TEXT) VALUES ('a', 'b')")
        con.commit()
    assert MOCK_TEXT_HANDLER._retrieve_text_by_id(text_id="a") == ["b"]
    remove_mock_db_if_it_exists()


def test_store_text_and_get_id():
    reset_mock_db()
    raw_now = datetime.now()
    now: datetime = datetime(
        raw_now.year,
        raw_now.month,
        raw_now.day,
        raw_now.hour,
        raw_now.minute,
        raw_now.second,
    )
    text_id = MOCK_TEXT_HANDLER.store_text_and_get_id(text=HELLO_TEXT)
    assert text_id == HELLO_TEXT_ID
    rows = get_all_rows()
    assert len(rows) == 1
    first_row = rows[0]
    assert first_row[0] == HELLO_TEXT_ID
    assert datetime.fromisoformat(first_row[1]) >= now
    assert first_row[2] == HELLO_TEXT

    # test idempotent behaviour
    assert MOCK_TEXT_HANDLER.store_text_and_get_id(text=HELLO_TEXT) == text_id
    assert get_all_rows() == rows
    remove_mock_db_if_it_exists()


def test_get_text_from_id():
    reset_mock_db()
    with pytest.raises(TextIdNotFoundError) as e:
        _ = MOCK_TEXT_HANDLER.get_text_from_id(text_id=HELLO_TEXT_ID)
        assert str(e) == f"No text stored under text id `{HELLO_TEXT_ID}`"

    with pytest.raises(TooManyTextsDbError):

        with patch(
            "tests.test_storage_utils.MOCK_TEXT_HANDLER._retrieve_text_by_id",
            return_value=["a", "b", "c"],
        ):
            _ = MOCK_TEXT_HANDLER.get_text_from_id(text_id=HELLO_TEXT_ID)

    with sqlite3.connect(MOCK_DB_NAME) as con:
        cur = con.cursor()
        cur.execute(
            f"insert into {TABLE_TEXTS} (TEXT_ID, TEXT)"
            f" VALUES ('{HELLO_TEXT_ID}', '{HELLO_TEXT}')"
        )
        con.commit()
    assert MOCK_TEXT_HANDLER.get_text_from_id(text_id=HELLO_TEXT_ID) == HELLO_TEXT
    remove_mock_db_if_it_exists()
