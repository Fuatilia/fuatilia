from utils.logger import logger
from db import run_db_transactions
from models.custom_permissions import (
    Permission,
    PermissionCreationBody,
    PermissionUpdateBody,
)
from utils.s3_utils import S3Processor

permission_s3_processor = S3Processor()


async def create_permission(create_body: PermissionCreationBody):
    data_to_initialize_permission = {
        "entity": create_body.entity,
        "permission": create_body.permission,
        "is_active": create_body.is_active,
    }

    try:
        logger.info(
            f"Permission creation with details ::  {data_to_initialize_permission}"
        )
        data = Permission(**data_to_initialize_permission)

        response = run_db_transactions("create", data, Permission)

        logger.info(response)

        return response

    except Exception as e:
        logger.exception(e)
        return {"error": e.__repr__()}


async def update_permission(update_body: PermissionUpdateBody):
    response = run_db_transactions(
        "update", update_body.model_dump(exclude_none=True), Permission
    )

    return response


async def filter_permissions(
    permissions_filter_body: any, page: int = 1, items_per_page: int = 5
):
    logger.info("Filter permissions ------------>")
    permissions_filter_body["limit"] = items_per_page
    permissions_filter_body["page"] = page
    response = run_db_transactions("get", permissions_filter_body, Permission)

    return response


async def delete_permission(id: str):
    """
    Parameters
    ----------
    id : str
        Id of the Permission

    Returns
    -------
    204 on successful deletion
    """
    logger.info(">>> Initiating delete for permission ", id)
    data = {"id": id}
    response = run_db_transactions("delete", data, Permission)
    return response
