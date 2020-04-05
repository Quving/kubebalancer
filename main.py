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

            # Check config syntax briefly.
            for key in ['interval', 'deployments', 'namespace']:
                if not key in config:
                    logger.error('Config.json is missing "{}" attribute. Please add it.'.format(key))
                    sys.exit(-1)

            valid_interval = isinstance(config['interval'], int) and config['interval'] > 0
            valid_deployments = isinstance(config['deployments'], list) and not bool([])
            valid_namespace = isinstance(config['namespace'], str) and not bool(config['namespace'])

            if not valid_interval and valid_deployments and valid_namespace:
                logger.error('Config.json is not valid. Please check it.')
                sys.exit(-1)

            pprint(config)
            print('\n')
            return config
    else:
        with open(config_file, 'w') as file:
            config = {
                'deployments': [],
                'interval': 0,
                'namespace': ''
            }
            json.dump(config, file, indent=4)

        logger.error('No config found. Please provide one by editing the generated config.json.')
        sys.exit(-1)


if __name__ == '__main__':
    config = get_config()
    api = KubeApi()
    api.watch_health(
        interval=config['interval'],
        namespace=config['namespace'],
        deployments=config['deployments']
    )
