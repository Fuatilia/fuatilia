import os
from services.files import file_upload
from db import run_db_transactions
from models.representatives import (
    FileType, Representative, 
    RepresentativeCreationBody, RepresentativeUpdateBody)
from utils.s3_utils import S3Processor
import traceback

# Initiate S3 processor
representative_s3_processor = S3Processor()

async def create_representative(create_body: RepresentativeCreationBody):
    data_to_initialize_represenatative  = {
        'full_name' : create_body.full_name ,
        'position' : create_body.position ,
        'position_type' : create_body.position_type ,
        'house' : create_body.house ,
        'area_represented' : create_body.area_represented ,
        'phone_number' : create_body.phone_number ,
        'gender' : create_body.gender ,
        'representation_summary' : create_body.representation_summary ,
    }

    try:
        print(f'Representative creation with details :: ', data_to_initialize_represenatative)
        data  = Representative(**data_to_initialize_represenatative)

        response = run_db_transactions('create',data, Representative)

        str_id = str(response['data']['id'])
        metadata = {
            'rep_id': str_id,
            'creation_date': response['data']['created_at'].strftime("%d/%m/%Y %H:%M:%S"),
            'source': create_body.image_source,
            'image_type': create_body.image_data_type,
            'use': 'For representative image/thumbnail',
            'representative_name': response['data']['full_name'],
            # 'content_type':
        }
        if response['status'] in [202, 200]:
            reps_data_bucket_name = os.environ.get('REPS_DATA_BUCKET_NAME')
            file_name = 'profile_image.jpeg'

            print('Initiating file upload --- > to S3' )
            if create_body.image_data_type == 'BASE64_ENCODING':
                # File path should allow for replacement of images
                s3_upload_response = await file_upload( 
                    reps_data_bucket_name, 
                    FileType.PROFILE_IMAGE,
                    file_name,
                    create_body.image_data,
                    id=response['data']['id'],
                    metadata = metadata
                )

                if s3_upload_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    image_url = f's3://{reps_data_bucket_name}/{response["data"]["id"]}/images/{file_name}'
                    response = run_db_transactions('update', 
                                                   {   'id' : response['data']['id'],
                                                       'image_url': image_url},
                                                    Representative)

            return response
        
    except Exception as e:
        traceback.print_exc()
        return {
            'error' : e.__repr__()
        }



async def update_representative(update_body:RepresentativeUpdateBody):
    
    response = run_db_transactions('update', 
                                    update_body.model_dump(exclude_none=True),
                                    Representative)
    
    return response


async def filter_representatives(representatives_filter_body: any, 
                                 page:int=1, items_per_page:int=5):
    print('Filter representataives ------------>')
    representatives_filter_body['limit'] = items_per_page
    response = run_db_transactions('get',representatives_filter_body, Representative)

    return response


async def delete_representative(id: str):
    """
    Parameters
    ----------
    id : str
        Id of the representative

    Returns
    -------
    204 on successful deletion
    """
    print(">>> Initiating delete for user ", id)
    data  = {'id':id}
    response = run_db_transactions('delete',data, Representative)
    return response



async def get_representative_files_list(id, file_type:FileType):
    """
    Parameters
    ----------
    id : str  Id of the representative
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


    Returns
    -------
    files : List[str]
        List of files as per specifed paths
    """
   
    bucket_name = os.environ.get('REPS_DATA_BUCKET_NAME')
    dir = representative_s3_processor.compute_s3_file_directory(file_type, '', id)
    
    try:
        files =  representative_s3_processor.get_bucket_file_list( bucket_name, dir)
        return files
    except Exception as e:
        return {
            'error': e.__repr__()
        }


async def get_file_data(file_name):
    response = representative_s3_processor.get_file(os.environ.get('REPS_DATA_BUCKET_NAME'), 
                                                    file_name)
    print(response)
    return response['Body'].read()


async def stream_file_data(file_name, start_KB, stop_KB):
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
    response = representative_s3_processor.get_file(os.environ.get('REPS_DATA_BUCKET_NAME'), 
                                                file_name, 
                                                range = 'bytes={}-{}'.format(
                                                    start_KB*1000, 
                                                    stop_KB*1000
                                                    ) 
                                                )
    return response['Body']


async def upload_representative_files(id:str, 
                                      file_type:FileType, 
                                      file_name:str, 
                                      base64encoding:str):
    
    bucket_name = os.environ.get('REPS_DATA_BUCKET_NAME')
    return await file_upload(bucket_name, file_type, file_name, base64encoding, id=id)
