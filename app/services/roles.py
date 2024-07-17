import re
from models.custom_permissions import Permission
from utils.logger import logger
from db import run_db_transactions
from models.roles import Role, RoleCreationBody, RoleUpdateBody


async def create_role(create_body: RoleCreationBody):
    try:
        permissions = []

        for permission_id in create_body.permissions:
            permission_data = run_db_transactions.get(
                "get", Permission, {"id": permission_id}
            )

            permissions.append(
                {
                    "entity": permission_data.entity,
                    "scope": re.search("^[^.]*", permission_data["permission"]).group(
                        0
                    ),
                    "permission": re.search(
                        "(?<=\\/).*$", permission_data["permission"]
                    ).group(0),
                    "effect": "Allow",
                }
            )

        data_to_initialize_role = {
            "permissions": permissions,
            "role": create_body.role,
        }
        logger.info(f"Role creation with details ::  {data_to_initialize_role}")
        data = Role(**data_to_initialize_role)

        response = run_db_transactions("create", data, Role)

        logger.info(response)

        return response

    except Exception as e:
        logger.exception(e)
        return {"error": e.__repr__()}


async def update_role(update_body: RoleUpdateBody):
    response = run_db_transactions(
        "update", update_body.model_dump(exclude_none=True), Role
    )

    return response


async def filter_roles(roles_filter_body: any, page: int = 1, items_per_page: int = 5):
    logger.info("Filter roles ------------>")
    roles_filter_body["limit"] = items_per_page
    roles_filter_body["page"] = page
    response = run_db_transactions("get", roles_filter_body, Role)

    return response


async def delete_role(id: str):
    """
    Parameters
    ----------
    id : str
        Id of the Role

    Returns
    -------
    204 on successful deletion
    """
    logger.info(">>> Initiating delete for role ", id)
    data = {"id": id}
    response = run_db_transactions("delete", data, Role)
    return response
