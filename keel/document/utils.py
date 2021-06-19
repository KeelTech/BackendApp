
from .constants import *
from keel.Core.helpers import upload_file_to_s3

def validate_files(file):
	err_msg = ''
	if file.size > MAX_FILE_SIZE:
		err_msg = MAX_FILE_SIZE_ERR_MSG
		return err_msg

	if not file.name.lower().endswith(tuple(ALLOWED_FILE_EXT)):
		err_msg = FILE_EXT_ERR_MSG
		return err_msg


def upload_files(files):

	err_msg = ''
	url_list = []

	if len(files) > MAX_ATTACHMENT_COUNT:
		err_msg = MAX_ATTACHMENT_ERR_MSG
		return err_msg, url_list

	for file in files.values():
		err_msg = validate_files(file)
		if err_msg:
			return err_msg, url_list

		url = upload_file_to_s3(file)
		url_list.append(url)

	return err_msg, url_list


