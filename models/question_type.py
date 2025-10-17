from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String

from config.db import meta

question_types = Table(
    "fs_question_types",
    meta,
    Column("id_question_type", Integer, primary_key=True),
    Column("question_type_name", String, nullable=False)
)