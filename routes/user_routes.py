from fastapi import APIRouter
from schemas.user import User

from controllers.user_controller import get_all_users, get_user_by_id, create_user

user = APIRouter(prefix="/users", tags=["Users"])


@user.get("/")
def get_users():
    return get_all_users()


@user.get("/{id}")
def get_user(id: int):
    return get_user_by_id(id)


@user.post("/")
def post_role(user: User):
    return create_user(user)
