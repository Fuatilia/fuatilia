from fastapi import APIRouter

from services.users import create_user, update_user, delete_user, filter_users
from models.users import UserCreationBody, UserUpdateBody

user_router = APIRouter(tags=["User"], prefix="/users")


@user_router.post("/create")
async def createUser(createBody: UserCreationBody):
    return await create_user(createBody)


@user_router.post("/login")
async def loginUser(createBody: UserCreationBody):
    # return await login_user(createBody)
    return NotImplementedError


@user_router.patch("/update")
async def updateUser(updateBody: UserUpdateBody):
    return await update_user(updateBody)


@user_router.get("")
async def filterUsers(
    id: str | None = None,
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
):
    # Covert QS to dict
    filter_params = {
        "id": id,
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
async def getUserById(id: str | None = None):
    return await filter_users({"id": id})


@user_router.delete("/{id}")
async def deleteUser(id: str = None):
    return await delete_user(id)
