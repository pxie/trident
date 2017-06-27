from trident import logger
log = logger.getLogger()

import os
import json


def test_ingestion():
    config = load_config()


def load_config():
    log.debug(os.getcwd())
    with open('config.json') as data_file:
        config = json.load(data_file)
    log.debug(config)

    return config
