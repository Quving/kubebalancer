import util
from kubeapi import KubeApi

if __name__ == '__main__':
    config = util.get_config()
    api = KubeApi()
    api.watch_health(
        node_label_selector=config['node_label_selector'],
        interval=config['interval'],
        namespace=config['namespace'],
        deployments=config['deployments']
    )
