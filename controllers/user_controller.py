import bcrypt
import random
import string

from fastapi import HTTPException
from sqlalchemy import select
from config.db import conn
from models.user import users
from models.role import roles
from schemas.user import User


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))


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
    ).select_from(j).order_by(users.c.id_user.asc())

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
            "user_state": row_dict["user_state"],
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


def create_user(user: User):
    random_password = generate_random_password(8)

    hashed_password = bcrypt.hashpw(
        random_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    new_user = user.model_dump(exclude_none=True)
    new_user["password"] = hashed_password

    stmt = users.insert().values(new_user).returning(users)
    result = conn.execute(stmt).fetchone()

    role_stmt = select(roles.c.id_role, roles.c.role_name).where(
        roles.c.id_role == result.id_role
    )
    role_result = conn.execute(role_stmt).fetchone()

    conn.commit()

    return {
        "id_user": result.id_user,
        "names": result.names,
        "last_names": result.last_names,
        "identification_type": result.identification_type,
        "identification": result.identification,
        "user_state": result.user_state,
        "role": {
            "id_role": role_result.id_role if role_result else None,
            "role_name": role_result.role_name if role_result else None,
        },
    }


def update_user(id: int, user: User):
    new_user = user.model_dump(exclude_none=True)

    stmt = users.update().where(users.c.id_user == id).values(new_user).returning(users)
    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    role_stmt = select(roles.c.id_role, roles.c.role_name).where(
        roles.c.id_role == result.id_role
    )
    role_result = conn.execute(role_stmt).fetchone()

    conn.commit()

    return {
        "id_user": result.id_user,
        "names": result.names,
        "last_names": result.last_names,
        "identification_type": result.identification_type,
        "identification": result.identification,
        "user_state": result.user_state,
        "role": {
            "id_role": role_result.id_role if role_result else None,
            "role_name": role_result.role_name if role_result else None,
        },
    }


def change_user_state(id: int):
    stmt = select(users).where(users.c.id_user == id)
    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    new_state = 0 if result.user_state == 1 else 1

    update_stmt = (
        users.update()
        .where(users.c.id_user == id)
        .values(user_state=new_state)
        .returning(users)
    )

    updated = conn.execute(update_stmt).fetchone()
    conn.commit()

    return updated.user_state


def delete_user(id: int):
    stmt = users.delete().where(users.c.id_user == id).returning(users)
    result = conn.execute(stmt).fetchone()
    conn.commit()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return result.id_user
