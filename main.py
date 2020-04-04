from kubeapi import KubeApi

if __name__ == '__main__':
    namespace = 'testing'
    deployments_to_deschedule = [
        'ares-api',
        'ares-worker',
        'eos-web',
        'horen',
        'medusa'
    ]

    api = KubeApi()
    api.watch_health(namespace=namespace, deployments=deployments_to_deschedule)
