from fastapi import APIRouter
# from schemas.role import Role
from controllers.user_controller import (
    get_all_users,
)

user = APIRouter(prefix="/users", tags=["Users"])


@user.get("/")
def get_roles():
    return get_all_users()