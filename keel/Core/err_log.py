
import logging
import json

logger = logging.getLogger('app-logger')

def log_error(severity, api_loc, user_id, **kwargs):

	logger.error( str(severity) + " - " + \
					str(api_loc) + " - " + \
					str(user_id) + " - " + \
					str(json.dumps(kwargs))
				)



