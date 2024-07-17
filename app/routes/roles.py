from models.roles import RoleCreationBody, RoleUpdateBody
from services.roles import create_role, delete_role, filter_roles, update_role
from fastapi import APIRouter

role_router = APIRouter(
    prefix="/roles",
    tags=["roles"],
)


@role_router.post("/v1/role/create")
async def createRole(create_body: RoleCreationBody):
    return await create_role(create_body)


@role_router.get("/v1/role/list")
async def filterRoles(
    name: str | None = None,
    page: int = 1,
    items_per_page: int = 10,
):
    filter_params = {
        "name": name,
    }
    return await filter_roles(filter_params, page, items_per_page)


@role_router.get("/v1/role/{id}")
async def filterRolesById(id: str):
    return await filter_roles({"id": id})


@role_router.patch("/v1/role")
async def updateRole():
    return await update_role(RoleUpdateBody)


@role_router.delete("/v1/role/{id}")
async def deleteRole(id: str):
    return delete_role({"id": id})
