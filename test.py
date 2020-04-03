import subprocess
import time

from kubernetes import client, config

from models import KubeNode

namespace = 'testing'
label_selector = 'grid=testing'


class KubeApi:
    def __init__(self):
        config.load_kube_config()

    def get_nodes(self, label_selector):
        """
        Returns a list of KubeNodes that is matched to the label selector.
        """
        print("Listing pods with their IPs:")
        api_client = client.CoreV1Api()
        ret = api_client.list_node(label_selector=label_selector)

        kubenodes = [KubeNode(node_json=node) for node in ret.items]

        return kubenodes

    def get_deployments(self, namespace):
        """
        Returns a list of deployment names within a specified namespace.
        """
        api_client = client.AppsV1Api()
        res = api_client.list_namespaced_deployment(namespace=namespace)
        return [r.metadata.name for r in res.items]

    def wait_for_deployment_complete(self, deployment_name, namespace, timeout=180):
        api = client.AppsV1Api()
        start = time.time()
        msg = ''
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
                msg_new = '[updated_replicas: {}, replicas: {}, available_replicas: {}, observed_generation: {}]' \
                    .format(s.updated_replicas, s.replicas - 1, s.available_replicas, s.observed_generation)
                if not msg == msg_new:
                    print(msg_new)
                    msg = msg_new

        raise RuntimeError(f'Waiting timeout for deployment {deployment_name}')

    def excute_shell_cmd(self, cmd_str):
        """
        Execute a given cmd on the shell, attaches the output and returns the exit value.
        """
        process = subprocess.Popen(cmd_str.split(), stdout=subprocess.PIPE, universal_newlines=True)
        while True:
            output = process.stdout.readline()
            print(output.strip())
            return_code = process.poll()
            if return_code is not None:
                return return_code

    def restart_rollout(self, deployment_name, namespace):
        """
        Restart a kubernetes rollout.
        """
        command = 'kubectl rollout restart deployment/{} -n {}'.format(deployment_name, namespace)
        self.excute_shell_cmd(command)


if __name__ == '__main__':
    kubeapi = KubeApi()
    # kubeapi.get_deployments(namespace='testing')
    # kubeapi.restart_rollout('eos-web', 'testing')
    # kubeapi.wait_for_deployment_complete('eos-web', 'testing')
