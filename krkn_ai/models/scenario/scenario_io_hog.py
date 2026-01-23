from collections import Counter
import json

from krkn_ai.utils.rng import rng
from krkn_ai.models.scenario.base import Scenario
from krkn_ai.models.scenario.parameters import (
    HogScenarioImageParameter,
    IOBlockSizeParameter,
    IOWorkersParameter,
    IOWriteBytesParameter,
    NamespaceParameter,
    NodeMountPathParameter,
    NodeSelectorParameter,
    NumberOfNodesParameter,
    TaintParameter,
    TotalChaosDurationParameter,
)
from krkn_ai.models.custom_errors import ScenarioParameterInitError


class NodeIOHogScenario(Scenario):
    name: str = "node-io-hog"
    krknctl_name: str = "node-io-hog"
    krknhub_image: str = "containers.krkn-chaos.dev/krkn-chaos/krkn-hub:node-io-hog"

    chaos_duration: TotalChaosDurationParameter = TotalChaosDurationParameter()
    io_block_size: IOBlockSizeParameter = IOBlockSizeParameter()
    io_workers: IOWorkersParameter = IOWorkersParameter()
    io_write_bytes: IOWriteBytesParameter = IOWriteBytesParameter()
    node_mount_path: NodeMountPathParameter = NodeMountPathParameter()
    namespace: NamespaceParameter = NamespaceParameter(value="default")
    node_selector: NodeSelectorParameter = NodeSelectorParameter()
    taint: TaintParameter = TaintParameter()
    number_of_nodes: NumberOfNodesParameter = NumberOfNodesParameter()
    hog_scenario_image: HogScenarioImageParameter = HogScenarioImageParameter()

    def __init__(self, **data):
        super().__init__(**data)
        self.mutate()

    @property
    def parameters(self):
        return [
            self.chaos_duration,
            self.io_block_size,
            self.io_workers,
            self.io_write_bytes,
            self.node_mount_path,
            self.namespace,
            self.node_selector,
            self.taint,
            self.number_of_nodes,
            self.hog_scenario_image,
        ]

    def mutate(self):
        nodes = self._cluster_components.nodes

        if len(nodes) == 0:
            raise ScenarioParameterInitError(
                "No nodes found in cluster components for node-io-hog scenario"
            )

        all_labels = Counter()
        for node in nodes:
            for label, value in node.labels.items():
                all_labels[f"{label}={value}"] += 1

        # scenario 1: Select a random node
        if rng.random() < 0.5 or len(all_labels) == 0:
            node = rng.choice(nodes)
            self.node_selector.value = f"kubernetes.io/hostname={node.name}"
            self.number_of_nodes.value = 1
            # Set taints for the selected node
            self.taint.value = json.dumps(node.taints) if node.taints else "[]"
        else:
            # scenario 2: Select a label
            label = rng.choice(list(all_labels.keys()))
            self.node_selector.value = label
            self.number_of_nodes.value = rng.randint(1, all_labels[label])

            # Get taints from matching nodes
            key, value = label.split("=", 1)
            matching_nodes = [n for n in nodes if n.labels.get(key) == value]

            # Collect all unique taints from matching nodes
            all_taints = []
            seen = set()
            for node in matching_nodes:
                if node.taints:
                    for taint in node.taints:
                        if taint not in seen:
                            seen.add(taint)
                            all_taints.append(taint)

            self.taint.value = json.dumps(all_taints) if all_taints else "[]"

        self.io_workers.mutate()
        self.io_write_bytes.mutate()
        self.io_block_size.mutate()
