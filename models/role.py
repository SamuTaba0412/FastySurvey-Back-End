from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Date

from config.db import meta, engine

roles = Table(
    "fs_roles",
    meta,
    Column("id_role", Integer, primary_key=True),
    Column("role_name", String(50), nullable=False),
    Column("creation_date", Date, nullable=False),
    Column("role_state", Integer, nullable=False, default=1),
    Column("update_date", Date)
)

meta.create_all(engine)