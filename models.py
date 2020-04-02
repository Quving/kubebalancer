import json


class KubeNode:
    def __init__(self, node_json):
        # Parse meta informations
        self.name = node_json.metadata.name
        self.uid = node_json.metadata.uid

        # Parse node conditions
        for condition_json in node_json.status.conditions:
            type = condition_json.type
            if type == 'MemoryPressure':
                self.memory_pressure = condition_json.status == 'True'

            if type == 'DiskPressure':
                self.disk_pressure = condition_json.status == 'True'

            if type == 'PIDPressure':
                self.pid_pressure = condition_json.status == 'True'

            if type == 'Ready':
                self.ready = condition_json.status == 'True'

    def __str__(self):
        attrs = {str(i): getattr(self, i) for i in dir(self) if not i.startswith('__')}
        return json.dumps(attrs)
