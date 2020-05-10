# KubeBalancer
## Problem
Currently there is no official configuration for the rescheduling problem of the pods within a Kubernetes cluster. The problem occurs after a Kubernetes node fails and the other nodes take up the services hosted by the failed node (Kubernetes self-healing mechanism). If this failed node comes back online, it will fall into an idle state because it does not "take back" the services as expected and therefore has no load. In the meantime the other nodes have a much too high load. The loads are not evenly distributed.


## Solution
This solution was developed from the given problem described above. This service is a running container that monitors the states of the Kubernetes nodes. If a node fails and comes back online after a certain time, specified pods are automatically redistributed (by specifying the deployment). Thus a load balance is restored. This solution can be used on all Kubernetes cluster environments.

This service does not have to run in a cluster, but can be hosted from anywhere where you can work with cli ```kubectl```.
## Setup and Configuration
### Kubernetes Authentication (Required)
In order for the status to be recorded by the Kubernetes nodes and for the rescheduling to work of course, the service must be authorized. A kube-config file is required for this. This service uses the same authentication method as kubectl.

So make sure that a valid kubeconfig file is located under ```~/.kube/config```.

### config.json (Required)
The configuration is done here via the config.json.
Example config.json
```json
{
  "interval": 3,
  "node_label_selector": "grid=testing",
  "namespace": "testing",
  "deployments": [
    "deployment-foo",
    "deployment-bar"
  ]
}
```

- **Interval**: In an interval of 3 seconds the status of the nodes is recorded. This means that after 3 seconds at the latest the automatic re-scheduling starts after a relevant node has come back online.
- **Node_Label_Selector**: This syntax follows the label_selector of Kubernetes and is used to configure which nodes are relevant and monitored.
- **Namespace**: The namespace specifies the scope of the pods to be rescheduled.
- **Deployments**: A list of deployment names, which are of course in the specified namespace, that should be rescheduled. 
    - If none specified (empty list) *n_deployments/m_nodes* random deployments will be selected in the specified namespace and will be rescheduled. 
    - m_nodes refers to the current number of available nodes during a check routine.
    - n_deployments includes all deployments in a given namespace. 

## healthy_state.json (Optional)
This JSON file specifies how the nodes are in a healthy initial state.
Example:
```json
[
    {
        "disk_pressure": false,
        "memory_pressure": false,
        "name": "k8s-node-1",
        "pid_pressure": false,
        "ready": true,
        "uid": "f50480c6-79f8-43b9-8cc2-abd22d2366c3"
    },
    {
        "disk_pressure": false,
        "memory_pressure": false,
        "name": "k8s-node-2",
        "pid_pressure": false,
        "ready": true,
        "uid": "f316b7f2-0fc1-4a19-a8cf-9c8f878d0f1c"
    },
    {
        "disk_pressure": false,
        "memory_pressure": false,
        "name": "k8s-node-3",
        "pid_pressure": false,
        "ready": true,
        "uid": "aafbab65-35f0-4d9e-a096-ac713303d427"
    }
]
```

If no health_state.json is specified, then the current state at the start of the service is taken as the healthy state and the rescheduling is based on this. The recorded state is then saved as healty_state.json. Editing while the service is running has no effect.

## Usage

1. Build docker-image
```bash docker build -t kubebalancer:latest . ```

2. Run the docker-container
```
docker run -d \
    --name kubebalancer \
    -v /path/to/config.json:/app/config.json \
    -v /path/to/kube/config:/root/.kube/config \
    kubebalancer:latest
```

