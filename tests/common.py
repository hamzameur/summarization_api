import os
from pathlib import Path
from summarization_api.storage_utils import SqlTextHandler, init_db

MOCK_DB_NAME: str = "mock.db"
MOCK_TEXT_HANDLER = SqlTextHandler(db_name=MOCK_DB_NAME)

HELLO_TEXT: str = "hello"
HELLO_TEXT_ID: str = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def reset_mock_db():
    remove_mock_db_if_it_exists()
    init_db(db_name=MOCK_DB_NAME)


def remove_mock_db_if_it_exists():
    db_path = Path(MOCK_DB_NAME)
    if db_path.is_file():
        os.remove(db_path)
