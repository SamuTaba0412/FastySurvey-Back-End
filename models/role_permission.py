from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from config.db import meta, engine

roles_permissions = Table(
    "fs_roles_permissions",
    meta,
    Column("id_roles_permissions", Integer, primary_key=True),
    Column(
        "id_role",
        Integer,
        ForeignKey(
            "fs_roles.id_role",
            ondelete="CASCADE",
            name="fk_role"
        )
    ),
    Column(
        "id_permission",
        Integer,
        ForeignKey(
            "fs_permissions.id_permission",
            ondelete="CASCADE",
            name="fk_permission"
        )
    ),
)

meta.create_all(engine)