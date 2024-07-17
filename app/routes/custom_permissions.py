from app.models.custom_permissions import PermissionCreationBody, PermissionUpdateBody
from app.services.custom_permissions import (
    create_permission,
    delete_permission,
    filter_permissions,
    update_permission,
)
from fastapi import APIRouter

permission_router = APIRouter(
    prefix="/permission",
    tags=["Permissions"],
)


@permission_router.post("/v1/create")
async def createPermission():
    return await create_permission(PermissionCreationBody)


@permission_router.get("/v1/list")
async def filterPermissions(filter_params):
    return await filter_permissions(filter_params)


@permission_router.get("/v1/{id}")
async def filterPermissionsById(id: str):
    return await filter_permissions({"id": id})


@permission_router.patch("/v1")
async def updatePermission():
    return await update_permission(PermissionUpdateBody)


@permission_router.delete("/v1/{id}")
async def deletePermission(id: str):
    return delete_permission({"id": id})
