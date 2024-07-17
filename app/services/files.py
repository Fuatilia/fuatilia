from utils.logger import logger
from utils.s3_utils import S3Processor
from utils.enum_utils import FileType

# Initiate S3 processor
representative_s3_processor = S3Processor()


async def file_upload(
    bucket_name: str, file_type: FileType, file_name, base64encoding, **kwargs
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
    metadata = kwargs.get("metadata")

    dir = representative_s3_processor.compute_s3_file_directory(
        file_type, file_name, id, house
    )

    try:
        response = representative_s3_processor.upload_file(
            base64encoding, bucket_name, file_name=dir, metadata=metadata
        )
        print(response)
        return response
    except Exception as e:
        logger.exception(e)
        return {"error": e.__repr__()}


async def get_file_data(bucket_name, file_name):
    response = representative_s3_processor.get_file(bucket_name, file_name)
    print(response)
    return response["Body"].read()


async def stream_file_data(bucket_name, file_name, start_KB, stop_KB):
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
