# KubeBalancer
## Problem
Currently there is no official configuration for the rescheduling problem of the pods within a Kubernetes cluster. The problem occurs after a Kubernetes node fails and the other nodes take up the services hosted by the failed node (Kubernetes self-healing mechanism). If this failed node comes back online, it will fall into an idle state because it does not "take back" the services as expected and therefore has no load. In the meantime the other nodes have a much too high load. The loads are not evenly distributed.


## Solution
This solution was developed from the given problem described above. This service is a running container that monitors the states of the Kubernetes nodes. If a node fails and comes back online after a certain time, specified pods are automatically redistributed (by specifying the deployment). Thus a load balance is restored. This solution can be used on all Kubernetes cluster environments.


## Setup
### Kubernetes Authentication



## Usage
... under construction ...

