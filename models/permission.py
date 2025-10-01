from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String

from config.db import meta, engine

permissions = Table(
    "fs_permissions",
    meta,
    Column("id_permission", Integer, primary_key=True),
    Column("permission_name", String, nullable=False)
)