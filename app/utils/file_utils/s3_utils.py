import logging
import re
import boto3
import os
import sys
import threading
import dotenv
from botocore.exceptions import ClientError
from utils.enum_utils import FileTypeEnum

dotenv.load_dotenv()
logger = logging.getLogger("app_logger")


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
                "\r%s  %s / %s  (%.2f%%)"
                % (self._filename, self._seen_so_far, self._size, percentage)
            )
            sys.stdout.flush()


class S3Processor:
    def __init__(self):
        self.region = os.environ.get("S3_BUCKET_REGION")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )

    def compute_s3_file_directory(
        self,
        file_type: FileTypeEnum,
        folder: str,
        file_name: str | None = None,
        id: str | None = None,
        house: str | None = None,
    ):
        """
        Based on the params passed it will compute the directory/filepath
        to get file(s) or add file(s)

        Parameters
        ----------
        file_type : str
            String of <class FileTypeEnum> do determine where the file goes

        file_name [Optional]:
                Name of the file. Will determine which file to save or get.
                If set to ALL during fetch with an ID specified, it will
                fetch all files in the directory

        id [Optional]:str
            Id of the the item (Mostly models)

        house [Optional]: str
            If passed will be paired with file type to get/put a file

        Returns
        --------
        string of the s3 file/directory path

        """

        logger.info(
            f"Computing file dir for type:{file_type}, name:{file_name} : id {id}, house : {house}"
        )
        match file_type:
            case FileTypeEnum.ALL:
                return f"{folder}/{id}/"
            case FileTypeEnum.IMAGE:
                return f"{folder}/{id}/images/" + file_name
            case FileTypeEnum.CASE:
                return f"{folder}/{id}/cases/" + file_name
            case FileTypeEnum.MANIFESTO:
                return f"{folder}/{id}/manifestos/" + file_name
            case FileTypeEnum.BILL:
                return f"{folder}/bills/{house}/" + file_name
            case FileTypeEnum.PROCEEDING:
                return f"{folder}/proceedings/{house}/" + file_name
            case FileTypeEnum.VOTE:
                return f"{folder}/votes/{house}/" + file_name

    def create_bucket(self, bucket_name, region=None):
        """
        Create an S3 bucket

        If a region is specified it will follow the s3 contrainsts as per S3 documentation

        Parameters
        ----------
        bucket_name: str
            Name of the bucket to create
        region [Optional]: str
            region to create bucket in, e.g., 'us-west-2'


        Returns
        -------
        S3 bucket creation response/error

        """

        # Create bucket
        try:
            if region is None:
                response = self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {"LocationConstraint": region}
                response = self.s3_client.create_bucket(
                    Bucket=bucket_name, CreateBucketConfiguration=location
                )
        except ClientError as e:
            logging.error(e)
            return e
        return response

    def upload_file(
        self,
        base64encoding_of_the_the_file,
        bucket,
        file_name=None,
        metadata=None,
        monitor_progress: bool = False,
    ):
        """
        Upload a file to an S3 bucket

        Parameters
        ----------
        base64encoding_of_the_the_file: str
            Base64 encoding of the file
        bucket:str
            Bucket to upload to
        file_name:str
            File name to assign on upload
        metadata: dict
            All metadata you need to add to the file.
            Ideally anything that allows referencing e.g. file sources etc.

        Return:
            S3 upload resposne or ClientError
        """

        try:
            logger.info(f"Initating file upload for :: {file_name} to {bucket}")
            if metadata is None:
                metadata = {}

            response = self.s3_client.put_object(
                # ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
                Body=base64encoding_of_the_the_file,
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
                Key=file_name,
                Metadata=metadata,
                # ServerSideEncryption='AES256'|'aws:kms'|'aws:kms:dsse',
                # StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'
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

            logger.info(f"File upload for {file_name} ---> {response}")

            if response.get("response"):
                if (
                    response["response"]["ResponseMetadata"]["HTTPStatusCode"] == 404
                    and response["response"]["Error"]["Code"] == "NoSuchBucket"
                ):
                    bucket_creation_response = self.create_bucket(bucket)

                if (
                    bucket_creation_response["ResponseMetadata"]["HTTPStatusCode"]
                    == 200
                ):
                    response = self.upload_file(
                        base64encoding_of_the_the_file,
                        bucket,
                        file_name=file_name,
                        metadata=metadata,
                    )
                else:
                    return bucket_creation_response

            return response
        except ClientError as e:
            logging.exception(e)
            return {"error": e.__repr__()}

    def update_file():
        return NotImplemented

    def remove_file(self):
        return NotImplemented

    def get_file(self, bucket_name, obj_name, range: str | None = None):
        """
        Get a stream response of the requested file

        Parameters
        ----------
        bucket_name: str
            Bucket to read from
        obj_name:str
            Full file path of the file to read
        range [Optional]: str
            Contains the range of bytes to get
            If not specified will, default retreaving the entire file at one go.


        Returns
        -------
        S3 stream or file object

        """
        if range:
            # For streaming
            response = self.s3_client.get_object(
                Bucket=bucket_name, Key=obj_name, Range=range
            )
        else:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=obj_name)
        return response

    def get_bucket_file_list(self, bucket_name, directory: str | None = None):
        """
        Parameters
        ----------
        bucket_name : str
            Bucket to search
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
        objects_list = self.s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=directory
        ).get("Contents")
        res = []
        # Iterate over every object in bucket
        if objects_list:
            for obj in objects_list:
                res.append(re.search("(?<=\\/).*$", obj["Key"]).group(0))

        return res

    def get_bucket_contents(self, bucket_name, directory: str | None = None):
        objects_list = self.s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=directory
        ).get("Contents")

        res = []

        # Iterate over every object in bucket
        for obj in objects_list:
            # Read an object from the bucket
            response = self.s3_client.get_object(Bucket=bucket_name, Key=obj["Key"])
            res.append(
                {
                    "file": obj["Key"],
                    "metadata": response["Metadata"],
                    "body": response["Body"],
                }
            )

        return res

    def download_file(
        self, bucket_name, object_name, file_name, monitor_progress: bool = True
    ):
        if monitor_progress:
            callback_func = ProgressPercentage(file_name or "file")
        else:
            callback_func = None

        return self.s3_client.download_file(
            bucket_name, object_name, file_name, Callback=callback_func
        )
