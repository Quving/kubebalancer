import time

from kubernetes import client, config

from models import KubeNode

namespace = 'testing'
label_selector = 'grid=testing'


class KubeApi:
    def __init__(self):
        config.load_kube_config()

    def get_nodes(self, label_selector):
        print("Listing pods with their IPs:")
        api_client = client.CoreV1Api()
        ret = api_client.list_node(label_selector=label_selector)

        kubenodes = [KubeNode(node_json=node) for node in ret.items]

        return kubenodes

    def get_deployments(self, namespace):
        api_client = client.AppsV1Api()
        res = api_client.list_namespaced_deployment(namespace=namespace)
        for r in res.items:
            print(r.metadata.name)

    def wait_for_deployment_complete(self, deployment_name, namespace, timeout=60):
        api = client.AppsV1Api()
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(2)
            response = api.read_namespaced_deployment_status(deployment_name, namespace)
            s = response.status
            if (s.updated_replicas == response.spec.replicas and
                    s.replicas == response.spec.replicas and
                    s.available_replicas == response.spec.replicas and
                    s.observed_generation >= response.metadata.generation):
                return True
            else:
                print(f'[updated_replicas:{s.updated_replicas},replicas:{s.replicas}'
                      ',available_replicas:{s.available_replicas},observed_generation:{s.observed_generation}] waiting...')

        raise RuntimeError(f'Waiting timeout for deployment {deployment_name}')

    # def restart_rollout(self, deployment_name, namespace):


if __name__ == '__main__':
    kubeapi = KubeApi()
    # kubeapi.get_deployments(namespace='testing')
    kubeapi.wait_for_deployment_complete('eos-web', 'testing')
