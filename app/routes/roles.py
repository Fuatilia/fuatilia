from models.roles import RoleCreationBody, RoleUpdateBody
from services.roles import create_role, delete_role, filter_roles, update_role
from fastapi import APIRouter, Security
from utils.auth import user_has_permissions

role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@role_router.post("/create")
async def createRole(
    create_body: RoleCreationBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["role_data_create"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await create_role(create_body)
    else:
        return permission_check_passed


@role_router.get("")
async def filterRoles(
    role: str | None = None,
    page: int = 1,
    items_per_page: int = 10,
):
    filter_params = {
        "role": role,
    }

    for key in filter_params.copy():
        if not filter_params[key]:
            filter_params.pop(key)

    return await filter_roles(filter_params, page, items_per_page)


@role_router.get("/{id}")
async def filterRolesById(id: str):
    return await filter_roles({"id": id})


@role_router.patch("/update")
async def updateRole(
    roleUpdateBody: RoleUpdateBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["role_data_update"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await update_role(roleUpdateBody)
    else:
        permission_check_passed


@role_router.delete("/{id}")
async def deleteRole(
    id: str,
    permission_check_passed=Security(
        user_has_permissions, scopes=["role_data_delete"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return delete_role({"id": id})
    else:
        permission_check_passed
