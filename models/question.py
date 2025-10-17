from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from config.db import meta

questions = Table(
    "fs_questions",
    meta,
    Column("id_question", Integer, primary_key=True),
    Column("question_name", String, nullable=False),
    Column(
        "id_section",
        Integer,
        ForeignKey(
            "fs_sections.id_section",
            name="fk_section"
        )
    ),
    Column(
        "id_question_type",
        Integer,
        ForeignKey(
            "fs_question_types.id_question_type",
            name="fk_question_type"
        )
    ),
)