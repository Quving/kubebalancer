from kubernetes import client, config

from models import KubeNode

label_selector = 'grid=testing'

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
ret = v1.list_node(label_selector=label_selector)

kubenodes = []
for node in ret.items:
    kubenodes.append(KubeNode(node_json=node))

for kn in kubenodes:
    print(kn)
