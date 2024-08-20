from utils.enum_utils import FileTypeEnum
from utils.file_utils.s3_utils import S3Processor
import logging

logger = logging.getLogger("app_logger")

# Initiate S3 processor
representative_s3_processor = S3Processor()


def file_upload(
    bucket_name: str, file_type: FileTypeEnum, file_name, base64encoding, **kwargs
):
    """
    id :  Id of the representative
    file_type : Allows you to select which files about the rep you want to retrive
            - Will determine which directories will be searched
    file_name : If specified , the specific file in the specified directory is what will be looked for
            - Pass file name as blank to get all file in the directory
            - Otherwise it will suffix the file name to the directory
    """

    id = kwargs.get("id")
    house = kwargs.get("house")
    folder = kwargs.get("folder")
    metadata = kwargs.get("metadata")

    dir = representative_s3_processor.compute_s3_file_directory(
        file_type, folder, file_name, id=id, house=house
    )

    try:
        response = representative_s3_processor.upload_file(
            base64encoding, bucket_name, file_name=dir, metadata=metadata
        )

        response = {**response, "file_url": f"s3://{bucket_name}/{dir}"}
        return response
    except Exception as e:
        logging.exception(e)
        return {"error": e.__repr__()}


def get_file_data(bucket_name, file_name):
    logger.info(f"Fetching file : {file_name}")
    response = representative_s3_processor.get_file(bucket_name, file_name)
    logger.info(response)
    return response["Body"].read()


def stream_file_data(bucket_name, file_name, start_KB, stop_KB):
    """
    Get a stream response of the requested file

    Parameters
    ----------
    file_name: str
        Full file path of the file to read
    start_KB: int
        Kilobyte(s) from where to start, To start at the begining , pass 0.
        Will be converted to bytes
    stop_KB: int
        Kilobyte(s) from where to stop. Will be converted to bytes


    Returns
    -------
    S3 stream object

    """
    response = representative_s3_processor.get_file(
        bucket_name,
        file_name,
        range="bytes={}-{}".format(start_KB * 1000, stop_KB * 1000),
    )
    return response["Body"]
