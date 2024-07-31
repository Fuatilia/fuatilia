from fastapi import APIRouter, Security
from utils.auth import user_has_permissions
from services.users import (
    create_user,
    login_user,
    update_user,
    delete_user,
    filter_users,
)
from models.users import UserLoginBody, UserCreationBody, UserUpdateBody

user_router = APIRouter(tags=["User"], prefix="/users")


@user_router.post("/create")
async def createUser(
    createBody: UserCreationBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["user_data_create"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await create_user(createBody)
    else:
        return permission_check_passed


@user_router.post("/login")
async def UserLoginBody(loginBody: UserLoginBody):
    return await login_user(loginBody)


@user_router.patch("/update")
async def updateUser(
    updateBody: UserUpdateBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["user_data_update"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await update_user(updateBody)
    else:
        return permission_check_passed


@user_router.get("")
async def filterUsers(
    first_name: str | None = None,
    age_start: int | None = None,
    age_end: int | None = None,
    user_type: str | None = None,
    last_name: str | None = None,
    phone_number: str | None = None,
    parent_organization: str | None = None,
    created_at_start: str | None = None,
    created_at_end: str | None = None,
    updated_at_start: str | None = None,
    updated_at_end: str | None = None,
    is_active: bool | None = None,
    cart: str | None = None,
    page: int = 1,
    items_per_page: int = 10,
    permission_check_passed=Security(
        user_has_permissions, scopes=["user_list_read"], use_cache=True
    ),
):
    if permission_check_passed is True:
        # Covert QS to dict
        filter_params = {
            "first_name": first_name,
            "age_start": age_start,
            "age_end": age_end,
            "user_type": user_type,
            "last_name": last_name,
            "phone_number": phone_number,
            "parent_organization": parent_organization,
            "created_at_start": created_at_start,
            "created_at_end": created_at_end,
            "updated_at_start": updated_at_start,
            "updated_at_end": updated_at_end,
            "is_active": is_active,
            "cart": cart,
        }

        for key in filter_params.copy():
            if not filter_params[key]:
                filter_params.pop(key)

        return await filter_users(filter_params, page, items_per_page)


@user_router.get("/{id}")
async def getUserById(
    id: str | None = None,
    permission_check_passed=Security(
        user_has_permissions, scopes=["user_data_read"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await filter_users({"id": id})
    else:
        return permission_check_passed


@user_router.delete("/{id}")
async def deleteUser(
    id: str = None,
    permission_check_passed=Security(
        user_has_permissions, scopes=["user_data_delete"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await delete_user(id)
    else:
        return permission_check_passed
