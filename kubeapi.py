import json
import logging
import os
import subprocess
import time

from kubernetes import client, config

from kubenode import KubeNode


class KubeApi:
    def __init__(self):
        config.load_kube_config()

        # Configure logger
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def get_nodes(self, label_selector):
        """
        Returns a list of KubeNodes that is matched to the label selector.
        """
        api_client = client.CoreV1Api()
        ret = api_client.list_node(label_selector=label_selector)

        kubenodes = [KubeNode.from_kubernetes_client(node_json=node) for node in ret.items]
        kubenodes = sorted(kubenodes, key=lambda k: k.name)
        return kubenodes

    def get_deployments(self, namespace):
        """
        Returns a list of deployment names within a specified namespace.
        """
        api_client = client.AppsV1Api()
        res = api_client.list_namespaced_deployment(namespace=namespace)
        return [r.metadata.name for r in res.items]

    def watch_rollout(self, deployment_name, namespace, timeout=180):
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

    def watch_health(self, namespace, deployments):
        # Settings
        interval = 3
        filename = 'nodes_health.json'
        label_selector = 'grid={}'.format(namespace)

        def save_kubenode_states_to_file(kubenodes):
            with open(filename, 'w') as file:
                json_dicts = [kn.to_dict() for kn in kubenodes]
                json.dump(json_dicts, file, indent=4)
            return kubenodes

        def load_kubenode_states_from_file():
            with open(filename, 'r') as file:
                return [KubeNode.from_dict(json) for json in json.load(file)]

        # Initially, the log file will be deleted to not have side effects.
        if os.path.exists(filename):
            os.remove(filename)

        kubenode_initial = self.get_nodes(label_selector)
        save_kubenode_states_to_file(kubenode_initial)

        self.logger.info('Start monitoring kubenodes.')
        self.logger.info('{} kubenode(s) are available and will be set as healthy state.'.format(len(kubenode_initial)))
        self.logger.info('The health will be checked in an interval of {} seconds.'.format(interval))

        while True:
            time.sleep(interval)
            kubenode_state_before = load_kubenode_states_from_file()
            kubenode_state_now = self.get_nodes(label_selector)

            n_nodes_ready_before = len([n for n in kubenode_state_before if n.ready])
            n_nodes_ready_now = len([n for n in kubenode_state_now if n.ready])

            # Detect if a node came only recently (since last check interval).
            diff = n_nodes_ready_before - n_nodes_ready_now
            if diff < 0:
                self.logger.info("{} node(s) came online since last check.".format(abs(diff)))
                for deployment in deployments:
                    self.restart_rollout(namespace=namespace, deployment_name=deployment)
                    self.watch_rollout(namespace=namespace, deployment_name=deployment)

            # Nothing is happening
            elif diff == 0:
                pass

            # Greater than equals 1 node went offline since last check.
            else:
                self.logger.info("{} node(s) went offline since last check.".format(abs(diff)))
                pass

            save_kubenode_states_to_file(kubenode_state_now)
