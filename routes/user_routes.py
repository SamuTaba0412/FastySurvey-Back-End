from fastapi import APIRouter
from schemas.user import User

from controllers.user_controller import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    change_user_state,
    delete_user
)

user = APIRouter(prefix="/users", tags=["Users"])


@user.get("/")
def get_users():
    return get_all_users()


@user.get("/{id}")
def get_user(id: int):
    return get_user_by_id(id)


@user.post("/")
def post_user(user: User):
    return create_user(user)


@user.put("/{id}")
def put_user(id: int, user: User):
    return update_user(id, user)


@user.put("/state/{id}")
def put_state_user(id: int):
    return change_user_state(id)

@user.delete("/{id}")
def delete_user(id: int):
    return delete_user(id)