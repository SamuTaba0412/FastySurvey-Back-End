from fastapi import HTTPException
from sqlalchemy import select
from config.db import conn
from models.role import roles
from models.permission import permissions
from models.role_permission import roles_permissions
from schemas.role import Role


def get_all_roles():
    j = roles.join(
        roles_permissions, roles.c.id_role == roles_permissions.c.id_role
    ).join(
        permissions, roles_permissions.c.id_permission == permissions.c.id_permission
    )

    stmt = (
        select(
            roles.c.id_role,
            roles.c.role_name,
            roles.c.creation_date,
            roles.c.role_state,
            roles.c.update_date,
            roles_permissions.c.id_permission,
            permissions.c.permission_name,
        )
        .select_from(j)
        .order_by(roles.c.id_role.asc())
    )

    result = conn.execute(stmt).fetchall()

    roles_dict = {}
    for row in result:
        role_id = row.id_role
        if role_id not in roles_dict:
            roles_dict[role_id] = {
                "id_role": role_id,
                "role_name": row.role_name,
                "creation_date": row.creation_date,
                "role_state": row.role_state,
                "update_date": row.update_date,
                "permissions": [],
            }
        roles_dict[role_id]["permissions"].append(
            {"id_permission": row.id_permission, "permission_name": row.permission_name}
        )

    return list(roles_dict.values())


def get_role_by_id(id: int):
    j = roles.join(
        roles_permissions, roles.c.id_role == roles_permissions.c.id_role
    ).join(
        permissions, roles_permissions.c.id_permission == permissions.c.id_permission
    )

    stmt = (
        select(
            roles.c.id_role,
            roles.c.role_name,
            roles.c.creation_date,
            roles.c.role_state,
            roles.c.update_date,
            roles_permissions.c.id_permission,
            permissions.c.permission_name,
        )
        .select_from(j)
        .where(roles.c.id_role == id)
    )

    result = conn.execute(stmt).fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="Role not found")

    # Convertimos las filas a diccionarios
    rows = [dict(row._mapping) for row in result]
    base = rows[0]

    return {
        "id_role": base["id_role"],
        "role_name": base["role_name"],
        "creation_date": base["creation_date"],
        "role_state": base["role_state"],
        "update_date": base["update_date"],
        "permissions": [
            {
                "id_permission": row["id_permission"],
                "permission_name": row["permission_name"],
            }
            for row in rows
        ],
    }


def create_role(role: Role):
    new_role = role.model_dump(exclude={"permissions"}, exclude_none=True)

    stmt = roles.insert().values(new_role).returning(roles)
    result = conn.execute(stmt).fetchone()
    role_id = result.id_role

    if role.permissions:
        perm_stmt = roles_permissions.insert().values(
            [{"id_role": role_id, "id_permission": perm} for perm in role.permissions]
        )
        conn.execute(perm_stmt)

    conn.commit()

    perm_query = (
        select(permissions.c.id_permission, permissions.c.permission_name)
        .join(
            roles_permissions,
            permissions.c.id_permission == roles_permissions.c.id_permission,
        )
        .where(roles_permissions.c.id_role == role_id)
    )

    perm_result = conn.execute(perm_query).fetchall()

    return {
        "id_role": role_id,
        "role_name": result.role_name,
        "creation_date": result.creation_date,
        "role_state": result.role_state,
        "update_date": result.update_date,
        "permissions": [
            {"id_permission": p.id_permission, "permission_name": p.permission_name}
            for p in perm_result
        ],
    }


def update_role(id: int, role: Role):
    new_role = role.model_dump(exclude={"permissions"}, exclude_none=True)

    stmt = roles.update().where(roles.c.id_role == id).values(new_role).returning(roles)
    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.permissions is not None:
        del_perm_stmt = roles_permissions.delete().where(
            (roles_permissions.c.id_role == id)
            & (~roles_permissions.c.id_permission.in_(role.permissions))
        )
        conn.execute(del_perm_stmt)

        existing_perms = conn.execute(
            select(roles_permissions.c.id_permission).where(
                roles_permissions.c.id_role == id
            )
        ).fetchall()

        existing_perm_ids = {p.id_permission for p in existing_perms}

        new_perms = [
            {"id_role": id, "id_permission": perm}
            for perm in role.permissions
            if perm not in existing_perm_ids
        ]
        if new_perms:
            conn.execute(roles_permissions.insert().values(new_perms))

    conn.commit()

    perms_stmt = (
        select(permissions.c.id_permission, permissions.c.permission_name)
        .select_from(
            roles_permissions.join(
                permissions,
                roles_permissions.c.id_permission == permissions.c.id_permission,
            )
        )
        .where(roles_permissions.c.id_role == id)
    )
    perms_result = conn.execute(perms_stmt).fetchall()

    return {
        "id_role": result.id_role,
        "role_name": result.role_name,
        "creation_date": result.creation_date,
        "role_state": result.role_state,
        "update_date": result.update_date,
        "permissions": [
            {"id_permission": p.id_permission, "permission_name": p.permission_name}
            for p in perms_result
        ],
    }


def change_role_state(id: int):
    stmt = select(roles).where(roles.c.id_role == id)
    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Role not found")

    new_state = 0 if result.role_state == 1 else 1

    update_stmt = (
        roles.update()
        .where(roles.c.id_role == id)
        .values(role_state=new_state)
        .returning(roles)
    )

    updated = conn.execute(update_stmt).fetchone()
    conn.commit()

    return updated.role_state


def delete_role_by_id(id: int):
    stmt = roles.delete().where(roles.c.id_role == id).returning(roles)
    result = conn.execute(stmt).fetchone()
    conn.commit()

    if not result:
        raise HTTPException(status_code=404, detail="Role not found")

    return result.id_role
