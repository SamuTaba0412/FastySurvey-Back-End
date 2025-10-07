from fastapi import APIRouter

# from schemas.role import Role
from controllers.user_controller import get_all_users, get_user_by_id

user = APIRouter(prefix="/users", tags=["Users"])


@user.get("/")
def get_users():
    return get_all_users()


@user.get("/{id}")
def get_user(id: int):
    return get_user_by_id(id)
