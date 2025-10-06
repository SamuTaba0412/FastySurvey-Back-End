from fastapi import APIRouter
from schemas.role import Role
from controllers.role_controller import (
    get_all_roles,
    get_role_by_id,
    create_role,
    update_role,
    change_role_state,
    delete_role,
)

role = APIRouter(prefix="/roles", tags=["Roles"])


@role.get("/")
def get_roles():
    return get_all_roles()


@role.get("/{id}")
def get_role(id: int):
    return get_role_by_id(id)


@role.post("/")
def post_role(role: Role):
    return create_role(role)


@role.put("/{id}")
def put_role(id: int, role: Role):
    return update_role(id, role)


@role.put("/state/{id}")
def put_role(id: int):
    return change_role_state(id)


@role.delete("/{id}")
def remove_role(id: int):
    return delete_role(id)
