from models.custom_permissions import PermissionCreationBody, PermissionUpdateBody
from services.custom_permissions import (
    create_permission,
    delete_permission,
    filter_permissions,
    update_permission,
)
from fastapi import APIRouter, Security
from utils.auth import user_has_permissions


permission_router = APIRouter(
    prefix="/permission",
    tags=["Permissions"],
)


@permission_router.post("/v1/create")
async def createPermission(
    create_body: PermissionCreationBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["permission_data_create"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await create_permission(create_body)
    else:
        return permission_check_passed


@permission_router.get("/v1/list")
async def filterPermissions(
    entity: str | None = None,
    permission: str | None = None,
    active: bool | None = None,
    page: int = 1,
    items_per_page: int = 10,
):
    filter_params = {"entity": entity, "permission": permission, "active": active}

    for key in filter_params.copy():
        if not filter_params[key]:
            filter_params.pop(key)

    return await filter_permissions(filter_params, page, items_per_page)


@permission_router.get("/v1/{id}")
async def filterPermissionsById(id: str):
    return await filter_permissions({"id": id})


@permission_router.patch("/v1")
async def updatePermission(
    update_body: PermissionUpdateBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["permission_data_update"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await update_permission(update_body)
    else:
        return permission_check_passed


@permission_router.delete("/v1/{id}")
async def deletePermission(
    id: str,
    permission_check_passed=Security(
        user_has_permissions, scopes=["permission_data_delete"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return delete_permission({"id": id})
    else:
        return permission_check_passed
