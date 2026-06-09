from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
create table if not exists files (
  path text primary key,
  size integer not null,
  mtime real not null,
  sha256 text not null,
  kind text not null,
  language text,
  is_large integer not null default 0,
  is_generated integer not null default 0
);
create table if not exists project (
  key text primary key,
  value text not null
);
create table if not exists commands (
  id integer primary key autoincrement,
  ts text not null default current_timestamp,
  command text not null,
  exit_code integer not null,
  duration_ms integer not null,
  stdout_bytes integer not null,
  stderr_bytes integer not null,
  output_path text
);
create table if not exists metrics (
  key text primary key,
  value integer not null default 0
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def increment(conn: sqlite3.Connection, key: str, amount: int = 1) -> None:
    conn.execute(
        "insert into metrics(key, value) values(?, ?) "
        "on conflict(key) do update set value = value + excluded.value",
        (key, amount),
    )
    conn.commit()
