import sqlite3
from hashlib import sha256

from typing import List

from summarization_api.model import (
    AbstractTextHandler,
    TextIdNotFoundError,
    TooManyTextsDbError,
)

TABLE_TEXTS: str = "TEXTS"
COL_TEXT: str = "TEXT"
COL_TEXT_ID: str = "TEXT_ID"
PARAM_TEXT: str = COL_TEXT.lower()
PARAM_TEXT_ID: str = COL_TEXT_ID.lower()


def get_text_hash(text: str) -> str:
    return sha256(text.encode()).hexdigest()


def init_db(db_name: str) -> None:
    with sqlite3.connect(db_name) as connection:
        with open("schema.sql") as f:
            connection.executescript(f.read())
        connection.commit()


class SqlTextHandler(AbstractTextHandler):
    def __init__(self, db_name: str):
        self.db_name: str = db_name

    def get_text_from_id(self, text_id: str) -> str:
        texts: List[str] = self._retrieve_text_by_id(text_id=text_id)
        if len(texts) == 0:
            raise TextIdNotFoundError(f"No text stored under text id `{text_id}`")
        if len(texts) > 1:
            raise TooManyTextsDbError(f"Too many texts found for text id `{text_id}`")
        return texts[0]

    def store_text_and_get_id(self, text: str) -> str:
        text_id: str = get_text_hash(text=text)
        text_id_rows = self._retrieve_text_by_id(text_id=text_id)
        if len(text_id_rows) == 0:
            self._insert_text_and_id(text, text_id)
        return text_id

    def _insert_text_and_id(self, text: str, text_id: str):
        insert_request: str = f"""INSERT INTO {TABLE_TEXTS} (
            {COL_TEXT_ID},
            {COL_TEXT}
        ) VALUES (
            :{PARAM_TEXT_ID},
            :{PARAM_TEXT}
        )
        """
        with self._get_db_connection() as connection:
            try:
                cur = connection.cursor()
                cur.execute(insert_request, {PARAM_TEXT: text, PARAM_TEXT_ID: text_id})
                connection.commit()
            except Exception as e:
                connection.rollback()
                raise e

    def _get_db_connection(self):
        return sqlite3.connect(self.db_name)

    def _retrieve_text_by_id(self, text_id: str) -> List[str]:
        with self._get_db_connection() as connection:
            cur = connection.cursor()
            query_results = cur.execute(
                f"SELECT {COL_TEXT} FROM {TABLE_TEXTS}"
                f" WHERE {COL_TEXT_ID} = :{PARAM_TEXT_ID}",
                {PARAM_TEXT_ID: text_id},
            ).fetchall()
        return list(map(lambda result: result[0], query_results))
