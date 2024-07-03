import datetime
import sys
from db import run_db_transactions
from models.representatives import Representative, RepresentativeCreationBody, RepresentativeUpdateBody
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
            reps_data_bucket_name = 'representatives-data'
            file_name = f'{str_id}/images/current_image.jpeg'

            print('Initiating file upload --- > to S3' )
            if create_body.image_data_type == 'BASE64_ENCODING':
                # File path should allow for replacement of images
                s3_upload_response = representative_s3_processor.upload_file(
                    create_body.image_data, reps_data_bucket_name, file_name= file_name, metadata = metadata
                )

                print(f'File upload for {str_id}/images/current_image.jpeg ---> {s3_upload_response}')
        
                if s3_upload_response.get('response') and (s3_upload_response['response']['ResponseMetadata']['HTTPStatusCode'] == 404 and
                    s3_upload_response['response']['Error']['Code'] == 'NoSuchBucket'):
                    bucket_creation_response = representative_s3_processor.create_bucket(reps_data_bucket_name )

                
                    if bucket_creation_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                        s3_upload_response = representative_s3_processor.upload_file(
                            create_body.image_data, reps_data_bucket_name, file_name= file_name, metadata = metadata
                        )
                    else:
                        return bucket_creation_response

                if s3_upload_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    response = run_db_transactions('update', 
                                                   {   'id' : response['data']['id'],
                                                       'image_url': f's3://{reps_data_bucket_name}/{file_name}'},
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
