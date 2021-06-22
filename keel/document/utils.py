import os

from .constants import *
from keel.Core.helpers import upload_file_to_s3

def validate_file_size(file):
    err_msg = ''
    if file.size > MAX_FILE_SIZE:
        err_msg = MAX_FILE_SIZE_ERR_MSG
        return err_msg

    if not file.name.lower().endswith(tuple(ALLOWED_FILE_EXT)):
        err_msg = FILE_EXT_ERR_MSG
        return err_msg


def validate_files(files):

    err_msg = ''

    if len(files) > MAX_ATTACHMENT_COUNT:
        err_msg = MAX_ATTACHMENT_ERR_MSG
        return err_msg

    for file in files.values():
        err_msg = validate_file_size(file)
        if err_msg:
            return err_msg
    return err_msg

def upload_files_to(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return str(instance.owner_id) + "/" + str(instance.doc_type) + "/" +str(instance.doc_pk) +filename_ext 


