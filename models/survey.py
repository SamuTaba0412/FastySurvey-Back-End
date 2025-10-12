from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Date, Text

from config.db import meta

surveys = Table(
    "fs_surveys",
    meta,
    Column("id_survey", Integer, primary_key=True),
    Column("survey_name", String(50), nullable=False),
    Column("creation_date", Date, nullable=False),
    Column("configuration_date", Date, nullable=True),
    Column("survey_state", Integer, nullable=False, default=1),
    Column("introductory_text", Text, nullable=True),
    Column("terms_conditions", Text, nullable=True)
)