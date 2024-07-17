import os
from utils.logger import logger
from services.files import file_upload
from db import run_db_transactions
from models.bills import Bill, BillCreationBody, BillUpdateBody
from utils.enum_utils import FileType
from utils.s3_utils import S3Processor

bill_s3_processor = S3Processor()


async def create_bill(create_body: BillCreationBody):
    data_to_initialize_bill = {
        "title": create_body.title,
        "status": create_body.status,
        "brought_forth_by": create_body.brought_forth_by,
        "supported_by": create_body.supported_by,
        "house": create_body.house,
        "summary": create_body.summary,
        "summary_created_by": create_body.summary_created_by,
        "summary_upvoted_by": create_body.summary_upvoted_by,
        "summary_downvoted_by": create_body.summary_downvoted_by,
        "final_date_voted": create_body.final_date_voted,
        "topics_in_the_bill": create_body.topics_in_the_bill,
    }

    try:
        logger.info(f"Bill creation with details ::  {data_to_initialize_bill}")
        data = Bill(**data_to_initialize_bill)

        response = run_db_transactions("create", data, Bill)

        logger.info(response)
        if response["status"] == 500:
            return response

        str_id = str(response["data"]["id"])
        metadata = {
            "rep_id": str_id,
            "creation_date": response["data"]["created_at"].strftime(
                "%d/%m/%Y %H:%M:%S"
            ),
            "source": create_body.file_source,
            "file_type": create_body.file_data_type,
            "use": "For bill file",
            "representative_name": response["data"]["title"],
            # 'content_type':
        }
        if response["status"] in [202, 200]:
            bills_data_bucket_name = f'{os.environ.get('BILLS_DATA_BUCKET_NAME')}'
            file_name = f'{response['data']['title']}.pdf'

            logger.info(f"Initiating file upload --- > to S3 {bills_data_bucket_name}")
            if create_body.file_data_type == "BASE64_ENCODING":
                # File path should allow for replacement of files'
                s3_upload_response = await file_upload(
                    bills_data_bucket_name,
                    FileType.BILL,
                    file_name,
                    create_body.file_data,
                    id=response["data"]["id"],
                    house=response["data"]["house"].value,
                    metadata=metadata,
                )

                if s3_upload_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    file_url = f"s3://{bills_data_bucket_name}/bill/{file_name}"
                    response = run_db_transactions(
                        "update",
                        {"id": response["data"]["id"], "file_url": file_url},
                        Bill,
                    )

            return response

    except Exception as e:
        logger.exception(e)
        return {"error": e.__repr__()}


async def update_bill(update_body: BillUpdateBody):
    response = run_db_transactions(
        "update", update_body.model_dump(exclude_none=True), Bill
    )

    return response


async def filter_bills(Bills_filter_body: any, page: int = 1, items_per_page: int = 5):
    logger.info("Filter bills ------------>")
    Bills_filter_body["limit"] = items_per_page
    Bills_filter_body["page"] = page

    response = run_db_transactions("get", Bills_filter_body, Bill)

    return response


async def delete_bill(id: str):
    """
    Parameters
    ----------
    id : str
        Id of the Bill

    Returns
    -------
    204 on successful deletion
    """
    logger.info(">>> Initiating delete for user ", id)
    data = {"id": id}
    response = run_db_transactions("delete", data, Bill)
    return response


async def get_bills_files_list(file_type: FileType, house: str = None):
    """
    Parameters
    ----------
    file_type : str
        Allows you to select which files about the rep you want to retrive
        Will determine which directories will be searched
        If set to ALL, for a path containing images/, manifestos/, cases/; All files
        in all directories will be returned with the respective directories prefixed
        e.g
        [
            "images/test.jpg",
            ...
            "cases/DPP_2022_Fetilizer.pdf",
            ...
        ]
    house : str
        national/senate. If left blank will return all files under the specified file type

    Returns
    -------
    files : List[str]
        List of files as per specifed paths
    """

    bucket_name = os.environ.get("BILLS_DATA_BUCKET_NAME")
    dir = bill_s3_processor.compute_s3_file_directory(file_type, "", house=house)

    try:
        files = bill_s3_processor.get_bucket_file_list(bucket_name, dir)
        return files
    except Exception as e:
        return {"error": e.__repr__()}
