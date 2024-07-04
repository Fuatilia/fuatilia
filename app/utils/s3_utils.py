import logging
import re
import boto3
import os
import sys
import threading
import dotenv
from botocore.exceptions import ClientError
from models.representatives import FileType

dotenv.load_dotenv()

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()



class S3Processor():
    def __init__(self):
        self.region = os.environ.get('S3_BUCKET_REGION')
        self.s3_client = boto3.client(
                's3', 
                aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
                 
    
    def compute_s3_file_directory(self, file_type:FileType, 
                              file_name:str|None = None, 
                              id:str|None = None, 
                              house:str|None = None):
        match file_type:
            case FileType.ALL:
                return f'{id}/'
            case FileType.PROFILE_IMAGE:
                return f'{id}/images/' + file_name
            case FileType.CASE:
                return f'{id}/cases/' + file_name
            case FileType.MANIFESTO:
                return f'{id}/manifestos/' + file_name
            case FileType.BILL:
                return f'bills/{house}/' + file_name
            case FileType.PROCEEDING:
                return f'proceedings/{house}/' + file_name
            case FileType.VOTE:
                return f'votes/{house}/' + file_name


    def create_bucket(self, bucket_name, region=None):
        '''
        Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        '''

        # Create bucket
        try:
            if region is None:
                response = self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': region}
                response  = self.s3_client.create_bucket(Bucket=bucket_name,
                                        CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return e
        return response


    def upload_file(
            self, 
            base64encoding_of_the_the_file, 
            bucket, file_name=None,
            metadata = None,
            monitor_progress:bool=False):
        '''
        Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        '''

        extra_args = {}

        try:
            print(f'Initating file upload for :: {file_name} to {bucket}')
            if monitor_progress:
                callback_func = ProgressPercentage(file_name or 'file')
            else:
                callback_func = None


            if metadata is None:
                metadata = {}

            response = self.s3_client.put_object(
                # ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
                Body= base64encoding_of_the_the_file ,
                Bucket=bucket,
                # CacheControl='string',
                # ContentDisposition='string',
                # ContentEncoding='string',
                # ContentLanguage='string',
                # ContentLength=123,
                # ContentMD5='string',
                # ContentType='string',
                # ChecksumAlgorithm='CRC32'|'CRC32C'|'SHA1'|'SHA256',
                # ChecksumCRC32='string',
                # ChecksumCRC32C='string',
                # ChecksumSHA1='string',
                # ChecksumSHA256='string',
                # Expires=datetime(2015, 1, 1),
                # GrantFullControl='string',
                # GrantRead='string',
                # GrantReadACP='string',
                # GrantWriteACP='string',
                Key= file_name,
                Metadata= metadata,
                # ServerSideEncryption='AES256'|'aws:kms'|'aws:kms:dsse',
                # StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS'|'GLACIER_IR'|'SNOW'|'EXPRESS_ONEZONE',
                # WebsiteRedirectLocation='string',
                # SSECustomerAlgorithm='string',
                # SSECustomerKey='string',
                # SSEKMSKeyId='string',
                # SSEKMSEncryptionContext='string',
                # BucketKeyEnabled=True|False,
                # RequestPayer='requester',
                # Tagging='string',
                # ObjectLockMode='GOVERNANCE'|'COMPLIANCE',
                # ObjectLockRetainUntilDate=datetime(2015, 1, 1),
                # ObjectLockLegalHoldStatus='ON'|'OFF',
                # ExpectedBucketOwner='string'
            )

            print(f'File upload for {file_name} ---> {response}')
        
            if response.get('response'):
                if (response['response']['ResponseMetadata']['HTTPStatusCode'] == 404 and
                    response['response']['Error']['Code'] == 'NoSuchBucket'):
                    bucket_creation_response = self.create_bucket(bucket)

            
                if bucket_creation_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    response = self.upload_file(
                        base64encoding_of_the_the_file, 
                        bucket, 
                        file_name= file_name, 
                        metadata = metadata
                    )
                else:
                    return bucket_creation_response
                

            return response
        except ClientError as e:
            logging.error(e)
            return e
        

    def update_file():
        return NotImplemented


    def remove_file(self):
        return NotImplemented


    def get_file(self, bucket_name, obj_name, range:str|None = None):
        if range:
            # For streaming
            response = self.s3_client.get_object(Bucket=bucket_name, Key=obj_name, Range=range)
        else:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=obj_name)
        return response
    

    def get_bucket_file_list(self, bucket_name, directory :str|None =None):
        objects_list = self.s3_client.list_objects_v2(Bucket=bucket_name,Prefix = directory).get("Contents")
        res  = []
        # Iterate over every object in bucket
        if objects_list:
            for obj in objects_list:
                res.append(re.search('(?<=\\/).*$', obj["Key"]).group(0))
        
        return res
    

    def get_bucket_contents(self, bucket_name, directory :str|None =None):        
        objects_list = self.s3_client.list_objects_v2(Bucket=bucket_name,Prefix = directory).get("Contents")

        res  = []

        # Iterate over every object in bucket
        for obj in objects_list:
            # Read an object from the bucket
            response = self.s3_client.get_object(Bucket=bucket_name, Key=obj["Key"])
            res.append({
                'file': obj["Key"],
                'metadata' : response['Metadata'],
                'body': response['Body']
            })
        
        return res

    
    def download_file(self, bucket_name, object_name, file_name):
        return self.s3_client.download_file(bucket_name, object_name, file_name)
