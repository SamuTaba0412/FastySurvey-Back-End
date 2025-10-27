from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from config.db import meta

options = Table(
    "fs_options",
    meta,
    Column("id_option", Integer, primary_key=True),
    Column("option_name", String, nullable=False),
    Column(
        "id_question",
        Integer,
        ForeignKey(
            "fs_questions.id_question",
            ondelete="CASCADE",
            name="fk_question"
        )
    ),
)