import os
import traceback
from utils.s3_utils import S3Processor
from models.representatives import FileType
# Initiate S3 processor
representative_s3_processor = S3Processor()

async def file_upload(bucket_name:str, file_type:FileType, file_name, base64encoding, **kwargs):
    '''
        id :  Id of the representative
        file_type : Allows you to select which files about the rep you want to retrive
                - Will determine which directories will be searched
        file_name : If specified , the specific file in the specified directory is what will be looked for
                - Pass file name as blank to get all file in the directory 
                - Otherwise it will suffix the file name to the directory
    '''

    id = kwargs.get('id')
    house = kwargs.get('house')
    metadata = kwargs.get('metadata')

    dir = representative_s3_processor.compute_s3_file_directory(file_type, file_name, id, house)

    try:
        response =  representative_s3_processor.upload_file(base64encoding, bucket_name, file_name=dir, metadata=metadata)
        print(response)
        return response
    except Exception as e:
        traceback.print_exc()
        return {
            'error': e.__repr__()
        }