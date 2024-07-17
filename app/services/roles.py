import traceback
from utils.logger import logger
from db import run_db_transactions
from models.roles import Role, RoleCreationBody, RoleUpdateBody


async def create_role(create_body: RoleCreationBody):
    data_to_initialize_role = {
        "entity": create_body.entity,
        "role": create_body.role,
        "is_active": create_body.is_active,
    }

    try:
        logger.info(f"Role creation with details ::  {data_to_initialize_role}")
        data = Role(**data_to_initialize_role)

        response = run_db_transactions("create", data, Role)

        logger.info(response)

        return response

    except Exception as e:
        traceback.print_exc()
        return {"error": e.__repr__()}


async def update_role(update_body: RoleUpdateBody):
    response = run_db_transactions(
        "update", update_body.model_dump(exclude_none=True), Role
    )

    return response


async def filter_roles(roles_filter_body: any, page: int = 1, items_per_page: int = 5):
    logger.info("Filter roles ------------>")
    roles_filter_body["limit"] = items_per_page
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
