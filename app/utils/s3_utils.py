import logging
import boto3
import os
import sys
import threading
import dotenv
from botocore.exceptions import ClientError

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
        self.s3_client = boto3.client('s3', region_name=self.region)
                 

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
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': region}
                self.s3_client.create_bucket(Bucket=bucket_name,
                                        CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True


    def upload_file(
            self, 
            base64encoding_of_the_the_file, 
            bucket, file_name=None, 
            object_name=None, 
            monitor_progress:bool=False):
        '''
        Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        '''

        try:
            if monitor_progress:
                callback_func = ProgressPercentage(file_name or 'file')
            else:
                callback_func = None
            response = self.s3_client.upload_file(
                base64encoding_of_the_the_file, 
                bucket, 
                object_name,
                Callback = callback_func
                )
            return response
        except ClientError as e:
            logging.error(e)
            return e
        

    def update_file():
        return NotImplemented


    def remove_file(self):
        return NotImplemented


    def get_file(self, bucket_name, obj_name):
        response = self.s3_client.get_object(Bucket=bucket_name, Key=obj_name)
        return response
    
    def get_bucket_contents(self, bucket_name):
        objects_list = self.s3_client.list_objects_v2(Bucket=bucket_name).get("Contents")

        res  = []

        # Iterate over every object in bucket
        for obj in objects_list:
            #  Store object name
            obj_name = obj["Key"]
            # Read an object from the bucket
            response = self.s3_client.get_object(Bucket=bucket_name, Key=obj_name)
            # Read the object’s content as text
            # object_content = response["Body"].read().decode("utf-8")
            res.append[response]
        
        return res

    
    def download_file(self, bucket_name, object_name, file_name):
        return self.s3_client.download_file(bucket_name, object_name, file_name)




