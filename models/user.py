from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Date

from config.db import meta

users = Table(
    "fs_users",
    meta,
    Column("id_user", Integer, primary_key=True),
    Column("names", String(60), nullable=False),
    Column("last_names", String(60), nullable=False),
    Column("identification_type", String(5), nullable=False),
    Column("identification", String(15), nullable=False, unique=True),
    Column("email", String(), nullable=False, unique=True),
    Column("creation_date", Date, nullable=False),
    Column("update_date", Date),
    Column("user_state", Integer, nullable=False, default=1),
    Column(
        "id_role",
        Integer,
        ForeignKey(
            "fs_roles.id_role",
            ondelete="CASCADE",
            name="fk_role"
        )
    ),
)