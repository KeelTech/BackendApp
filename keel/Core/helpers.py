import uuid
import os
import boto3

from urllib.parse import urlparse

from config.settings.production import (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, 
                                    AWS_S3_REGION, AWS_STORAGE_BUCKET_NAME)

def get_s3_confing():
    s3_config =  boto3.resource('s3',
                             region_name=AWS_S3_REGION,
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                            )                           
    return s3_config

def generate_unique_id(prefix):
    return prefix + str(uuid.uuid4())


def upload_file_to_s3(file):
    project_path = os.path.abspath(os.path.join(os.path.dirname( __name__ ), '.'))
    file_path = project_path + "/UserDocuments/"

    if not os.path.exists(file_path):
        os.mkdir(file_path)

    parsed = urlparse(file.name)
    root, ext = os.path.splitext(parsed.path)
    if not ext:
        try:
            ext = "." + file.name.split(".")[-1]
        except Exception as e:
            ext = ""

    file_name = generate_unique_id('doc_') + ext
    file_full_path = file_path + file_name
    f = open(file_full_path, 'wb')
    f.write(file.read())
    f.close()
    s3_config = get_s3_confing()
    response = s3_config.meta.client.upload_file(
                                file_full_path, 
                                S3_BUCKET_NAME, 
                                "/UserDocuments/"+file_name
                                )
    ## return with URLs
    return


