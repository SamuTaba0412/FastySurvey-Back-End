from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from config.db import meta

sections = Table(
    "fs_sections",
    meta,
    Column("id_section", Integer, primary_key=True),
    Column("section_name", String, nullable=False),
    Column(
        "id_survey",
        Integer,
        ForeignKey(
            "fs_surveys.id_survey",
            ondelete="CASCADE",
            name="fk_section"
        )
    ),
)