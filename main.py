import json
import os
import sys
from pprint import pprint

from kubeapi import KubeApi
from logger import Logger

logger = Logger.logger


def get_config():
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            logger.info('Config found:\n')
            pprint(config)
            print('\n')
    else:
        with open(config_file, 'w') as file:
            config = {'namespace': '', 'deployments': []}
            json.dump(config, file, indent=4)

        logger.error('No config found. Please provide one by editing the config.json.')
        sys.exit(-1)

    return config


if __name__ == '__main__':
    config = get_config()
    api = KubeApi()
    api.watch_health(
        namespace=config['namespace'],
        deployments=config['deployments'])
