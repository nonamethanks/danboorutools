from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import peewee

from danboorutools import logger

if TYPE_CHECKING:

    from collections.abc import Iterable

    from google.cloud import bigquery


def execute_bigquery_query(query_string: str) -> Iterable[bigquery.Row]:
    from google.cloud import bigquery

    client = bigquery.Client()

    logger.debug(f"Executing query: '{query_string.replace("\n", " ")}'")
    query = client.query(query_string)

    return query.result()


def clone_bigquery_table(table_name: str, model: type[peewee.Model], database: peewee.SqliteDatabase) -> None:
    with database:
        database.create_tables([model])

    if not (current_count := model.select().count()):
        logger.info("Creating the database from scratch...")
        last_checked = None
    else:
        last_checked_object = model.select().order_by(model.updated_at.desc()).get()  # type: ignore[attr-defined]
        last_updated_str = last_checked_object.updated_at
        last_checked = datetime.datetime.fromisoformat(last_updated_str)
        logger.info(f"There are already {current_count} rows in the DB. Populating from last updated_at: {last_checked}")

    column_names = [field.name for field in model._meta.fields.values()]  # type: ignore[attr-defined]

    query = f"SELECT {",".join(column_names)} FROM `danbooru1.danbooru_public.{table_name}`"  # noqa: S608
    if last_checked:
        query += f" WHERE updated_at >= TIMESTAMP_MILLIS({int(last_checked.timestamp() * 1000)})"
    query += " ORDER BY updated_at ASC, id"

    tags = execute_bigquery_query(query)

    updated = 0

    to_process: list[bigquery.Row] = []
    for index, tag in enumerate(tags):
        to_process += [tag]
        if index > 0 and index % 10_000 == 0:
            logger.debug(f"At tag {index}, date: {tag.updated_at}...")
            updated += len(to_process)
            update_db(to_process, model, database)
            to_process = []

    updated += len(to_process)
    update_db(to_process, model, database)

    logger.info(f"Updated {updated} rows.")


def update_db(rows: list[bigquery.Row], model: type[peewee.Model], database: peewee.SqliteDatabase) -> None:
    if not rows:
        return
    logger.debug(f"Inserting {len(rows)} rows...")
    row_enum = (dict(row) for row in rows)
    with database.atomic():
        model.replace_many(row_enum).execute()
