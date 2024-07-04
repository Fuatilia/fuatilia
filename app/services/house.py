import os
from models.representatives import FileType
from utils.s3_utils import S3Processor
import traceback

# Initiate S3 processor
representative_s3_processor = S3Processor()


async def get_house_file_objects(file_type:FileType, house:str, file_name:str|None = None):
    file_name = file_name or ''
    bucket_name = os.environ.get('HOUSE_DATA_BUCKET_NAME')

    dir  = representative_s3_processor.compute_s3_file_directory(file_type, file_name, None, house)

    if file_name == '':
        return representative_s3_processor.get_bucket_contents( bucket_name, dir)
    else:
        return representative_s3_processor.get_file(bucket_name, dir)