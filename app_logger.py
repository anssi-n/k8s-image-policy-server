import logging
import logging.config
import json

def configure_logger():
    with open("logging_config.json","r",encoding="utf-8") as f:
        config = json.load(f)
        logging.config.dictConfig(config)

configure_logger()   
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

