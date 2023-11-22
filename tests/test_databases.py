"""Test database config."""
# pylint: disable=import-error, unspecified-encoding
import os
import sqlite3 as sql
import re
import pandas as pd
from helper_io import load_config

CFG = load_config()


def test_database_schema() -> None:
    """"Tests if database has correct schema."""
    path = os.path.join(CFG["WORKSPACE"], 'data/activity.db')
    conn = sql.connect(path)
    schemas = pd.read_sql("SELECT name, sql FROM sqlite_master", conn)
    conn.close()

    for _, row in schemas.iterrows():
        schema_path = os.path.join(
            CFG["WORKSPACE"], f'schema/{row["name"]}_schema.sql'
        )
        with open(schema_path, 'r') as file:
            schema = re.sub(r'\s+', ' ', file.read()).strip()
        assert schema == re.sub(r'\s+', ' ', row["sql"]).strip()
