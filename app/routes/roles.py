from app.models.roles import RoleCreationBody, RoleUpdateBody
from app.services.roles import create_role, delete_role, filter_roles, update_role
from fastapi import APIRouter

roles_router = APIRouter(
    prefix="/roles",
    tags=["roles"],
)


@roles_router.post("/v1/role/create")
async def createRole():
    return await create_role(RoleCreationBody)


@roles_router.get("/v1/role/list")
async def filterRoles(filter_params):
    return await filter_roles(filter_params)


@roles_router.get("/v1/role/{id}")
async def filterRolesById(id: str):
    return await filter_roles({"id": id})


@roles_router.patch("/v1/role")
async def updateRole():
    return await update_role(RoleUpdateBody)


@roles_router.delete("/v1/role/{id}")
async def deleteRole(id: str):
    return delete_role({"id": id})
