from collections import Counter

from krkn_ai.utils.rng import rng
from krkn_ai.models.scenario.base import Scenario
from krkn_ai.models.scenario.parameters import *
from krkn_ai.models.custom_errors import ScenarioParameterInitError
from krkn_ai.models.cluster_components import Namespace, VMI
from typing import List, Tuple, Optional

class KubevirtDisruptionScenario(Scenario):
    name: str = "kubevirt-outage"
    krknctl_name: str = "kubevirt-outage"
    krknhub_image: str = "containers.krkn-chaos.dev/krkn-chaos/krkn-hub:kubevirt-outage"

    timeout: TimeoutParameter = TimeoutParameter()
    vm_name: VMNameParameter = VMNameParameter()
    namespace: NamespaceParameter = NamespaceParameter()
    kill_count: KillCountParameter = KillCountParameter()
    
    def __init__(self, **data):
        super().__init__(**data)
        self.mutate()

    @property
    def parameters(self):
        return [
            self.timeout,
            self.vm_name,
            self.namespace,
            self.kill_count,
        ]

    def mutate(self):

        if len(self._cluster_components.namespaces) == 0:
            raise ScenarioParameterInitError("No namespaces found in cluster components")
        
        namespaces = List[Tuple[Namespace, VMI]] = []  # (namespace, vm)
        
        for ns in self._cluster_components.namespaces:
            if len(ns.vms) > 0:
                namespaces.extend((ns, vmi) for vmi in namespace.vmis)

        # Check availability before mutation - skip test if no vms found
        if not namespaces:
            raise ScenarioParameterInitError("No VMS found in cluster components for KubeVirt scenario")
        
        namespace, vmis = rng.choice(namespaces)
        self.vm_name.value = vmis.name
        self.namespace.value = namespace.name
        self.kill_count =  rng.randint(1, len(namespace.vmis))

