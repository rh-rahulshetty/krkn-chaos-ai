from collections import Counter
import json
from typing import List

from krkn_ai.models.cluster_components import Node
from krkn_ai.models.custom_errors import ScenarioParameterInitError
from krkn_ai.utils.rng import rng
from krkn_ai.models.scenario.base import Scenario
from krkn_ai.models.scenario.parameters import *


class NodeMemoryHogScenario(Scenario):
    name: str = "node-memory-hog"
    krknctl_name: str = "node-memory-hog"
    krknhub_image: str = "containers.krkn-chaos.dev/krkn-chaos/krkn-hub:node-memory-hog"

    chaos_duration: TotalChaosDurationParameter = TotalChaosDurationParameter()
    node_memory_percentage: NodeMemoryPercentageParameter = NodeMemoryPercentageParameter()
    number_of_workers: NumberOfWorkersParameter = NumberOfWorkersParameter()
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
            self.node_memory_percentage,
            self.number_of_workers,
            self.node_selector,
            self.taint,
            self.number_of_nodes,
            self.hog_scenario_image,
        ]

    def mutate(self):
        nodes = self._cluster_components.nodes
    
        if len(nodes) == 0:
            raise ScenarioParameterInitError("No nodes found in cluster components")

        all_node_labels = Counter()
        for node in nodes:
            for label, value in node.labels.items():
                all_node_labels[f"{label}={value}"] += 1

        if rng.random() < 0.5 or len(all_node_labels) == 0:
            # case 1: Select a random node
            node = rng.choice(nodes)
            self.select_by_node(node)
        else:
            # case 2: Select a label
            label = rng.choice(list(all_node_labels.keys()))
            self.select_by_label(label, all_node_labels, nodes)

        self.number_of_workers.mutate()
        self.node_memory_percentage.mutate()

    
    def select_by_node(self, node: Node):
        self.node_selector.value = f"kubernetes.io/hostname={node.name}"
        self.number_of_nodes.value = 1
        # Set taints for the selected node
        self.taint.value = json.dumps(node.taints) if node.taints else '[]'


    def select_by_label(self, label: str, all_node_labels: Counter, nodes: List[Node]):
        self.node_selector.value = label
        self.number_of_nodes.value = rng.randint(1, all_node_labels[label])

        # Get taints from matching nodes
        key, value = label.split('=', 1)
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
        
        self.taint.value = json.dumps(all_taints) if all_taints else '[]'