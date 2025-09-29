from fastapi import APIRouter, HTTPException

# from cryptography.fernet import Fernet

from config.db import conn
from models.role import roles

from schemas.role import Role

# key = Fernet.generate_key()
# f = Fernet(key)

role = APIRouter(prefix="/roles", tags=["Roles"])


@role.get("/")
def get_roles():
    result = conn.execute(roles.select()).fetchall()
    return [dict(row._mapping) for row in result]


@role.get("/{id}")
def get_role(id: int):
    stmt = roles.select().where(roles.c.id_role == id)

    row = conn.execute(stmt).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Role not found")

    return dict(row._mapping)


@role.post("/")
def create_role(role: Role):
    stmt = roles.insert().values(role.model_dump(exclude_none=True)).returning(roles)

    row = conn.execute(stmt).fetchone()
    conn.commit()

    return dict(row._mapping)


@role.put("/{id}")
def update_role(id: int, role: Role):
    stmt = (
        roles.update()
        .where(roles.c.id_role == id)
        .values(role.model_dump(exclude_none=True))
        .returning(roles)
    )

    row = conn.execute(stmt).fetchone()
    conn.commit()

    if not row:
        raise HTTPException(status_code=404, detail="Role not found")

    return dict(row._mapping)


@role.delete("/{id}")
def delete_role(id: int):
    stmt = roles.delete().where(roles.c.id_role == id).returning(roles)
    row = conn.execute(stmt).fetchone()
    conn.commit()

    if not row:
        raise HTTPException(status_code=404, detail="Role not found")

    return dict(row._mapping)