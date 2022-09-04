DROP TABLE IF EXISTS texts;

CREATE TABLE texts (
    text_id TEXT PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
    text TEXT NOT NULL
);
