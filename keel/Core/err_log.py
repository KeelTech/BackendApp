
import logging

logger = logging.getLogger('app-logger')


def logging_format(severity, api_loc, user_id, **kwargs):
	log_msg = "{} - {} - {}".format(api_loc, user_id, kwargs)
	if severity:
		log_msg = str(severity) + " - " + log_msg
	return log_msg


def log_error(severity, api_loc, user_id, **kwargs):
	logger.error(logging_format(severity, api_loc, user_id, **kwargs))

