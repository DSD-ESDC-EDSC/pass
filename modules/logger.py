import logging

# when running app
try:
	from modules import config

# when running InitSchema
except:
	import config

def init():
	log_levels = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL,
	}
	
	LOGGER_DEFAULT_LEVEL = config.Logger().DEFAULT_LEVEL

	# initialize logging
	if config.Logger().FILE.lower() == "true":
		logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', filename=config.Logger().FILE_PATH, filemode='a', level=logging.DEBUG)
	else:
		logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)
		
	logger = logging.getLogger(__name__)
	logger.setLevel(log_levels.get(LOGGER_DEFAULT_LEVEL, logging.INFO))

	return logger
