import os
from utils.logger import logger
from db import run_db_transactions
from models.votes import Vote, VoteCreationBody, VoteUpdateBody
from utils.enum_utils import FileType
from utils.s3_utils import S3Processor

vote_s3_processor = S3Processor()


async def create_vote(create_body: VoteCreationBody):
    data_to_initialize_vote = {
        "bill_id": create_body.bill_id,
        "representative_id": create_body.representative_id,
        "house": create_body.house,
        "vote": create_body.vote,
        "vote_type": create_body.vote_type,
        "vote_summary": create_body.vote_summary,
    }

    try:
        logger.info(f"Vote creation with details ::  {data_to_initialize_vote}")
        data = Vote(**data_to_initialize_vote)

        response = run_db_transactions("create", data, Vote)

        logger.info(response)

        return response

    except Exception as e:
        logger.exception(e)
        return {"error": e.__repr__()}


async def update_vote(update_body: VoteUpdateBody):
    response = run_db_transactions(
        "update", update_body.model_dump(exclude_none=True), Vote
    )

    return response


async def filter_votes(votes_filter_body: any, page: int = 1, items_per_page: int = 5):
    logger.info("Filter bills ------------>")
    votes_filter_body["limit"] = items_per_page
    votes_filter_body["page"] = page
    response = run_db_transactions("get", votes_filter_body, Vote)

    return response


async def delete_vote(id: str):
    """
    Parameters
    ----------
    id : str
        Id of the Vote

    Returns
    -------
    204 on successful deletion
    """
    logger.info(">>> Initiating delete for vote ", id)
    data = {"id": id}
    response = run_db_transactions("delete", data, Vote)
    return response


async def get_votes_files_list(file_type: FileType, house: str = None):
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

    bucket_name = os.environ.get("VOTES_DATA_BUCKET_NAME")
    dir = vote_s3_processor.compute_s3_file_directory(file_type, "", house=house)

    try:
        files = vote_s3_processor.get_bucket_file_list(bucket_name, dir)
        return files
    except Exception as e:
        return {"error": e.__repr__()}
