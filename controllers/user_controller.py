from fastapi import HTTPException
from sqlalchemy import select
from config.db import conn
from models.user import users
from models.role import roles


def get_all_users():
    j = users.join(roles, users.c.id_role == roles.c.id_role)

    stmt = select(
        users.c.id_user,
        users.c.names,
        users.c.last_names,
        users.c.identification_type,
        users.c.identification,
        users.c.user_state,
        roles.c.id_role,
        roles.c.role_name,
    ).select_from(j)

    result = conn.execute(stmt).fetchall()

    users_list = []
    for row in result:
        row_dict = dict(row._mapping)

        user_data = {
            "id_user": row_dict["id_user"],
            "names": row_dict["names"],
            "last_names": row_dict["last_names"],
            "identification_type": row_dict["identification_type"],
            "identification": row_dict["identification"],
            "role": {
                "id_role": row_dict["id_role"],
                "role_name": row_dict["role_name"],
            },
        }

        users_list.append(user_data)

    return users_list


def get_user_by_id(id: int):
    j = users.join(roles, users.c.id_role == roles.c.id_role)

    stmt = (
        select(
            users.c.id_user,
            users.c.names,
            users.c.last_names,
            users.c.identification_type,
            users.c.identification,
            users.c.email,
            users.c.creation_date,
            users.c.update_date,
            users.c.user_state,
            roles.c.id_role,
            roles.c.role_name,
        )
        .select_from(j)
        .where(users.c.id_user == id)
    )

    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Role not found")

    row = dict(result._mapping)

    return {
        "id_user": row["id_user"],
        "names": row["names"],
        "last_names": row["last_names"],
        "identification_type": row["identification_type"],
        "identification": row["identification"],
        "email": row["email"],
        "creation_date": row["creation_date"],
        "update_date": row["update_date"],
        "user_state": row["user_state"],
        "role": {"id_role": row["id_role"], "role_name": row["role_name"]},
    }
