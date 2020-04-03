from kubeapi import KubeApi

"""
This is an example how to restart a rollout of kubernetes workload. 
Please make sure to follow the setup step before executing this script.
"""

if __name__ == '__main__':
    # Specification of the workload that is to be redeployed.
    namespace = 'testing'
    deployment = 'eos-web'

    kubeapi = KubeApi()
    kubeapi.restart_rollout(
        deployment_name=deployment,
        namespace=namespace
    )
    kubeapi.watch_rollout(
        deployment_name=deployment,
        namespace=namespace
    )
