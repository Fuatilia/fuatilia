from models.roles import RoleCreationBody, RoleUpdateBody
from services.roles import create_role, delete_role, filter_roles, update_role
from fastapi import APIRouter

role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@role_router.post("/create")
async def createRole(create_body: RoleCreationBody):
    return await create_role(create_body)


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
async def updateRole():
    return await update_role(RoleUpdateBody)


@role_router.delete("/{id}")
async def deleteRole(id: str):
    return delete_role({"id": id})
