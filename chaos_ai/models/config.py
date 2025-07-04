from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import chaos_ai.constants as const


class PodScenarioConfig(BaseModel):
    namespace: List[str] = ["openshift-.*"]
    pod_label: List[str] = [""]
    name_pattern: List[str] = [".*"]


class AppOutageScenarioConfig(BaseModel):
    namespace: List[str] = []
    pod_selector: List[str] = []


class ContainerScenarioConfig(BaseModel):
    namespace: List[str] = []
    label_selector: List[str] = []
    container_name: List[str] = []


class NodeHogScenarioConfig(BaseModel):
    node_selector: List[str] = []
    taints: List[str] = []


class ScenarioConfig(BaseModel):
    application_outages: Optional[AppOutageScenarioConfig] = Field(
        alias="application-outages", default=None
    )
    pod_scenarios: Optional[PodScenarioConfig] = Field(
        alias="pod-scenarios", default=None
    )
    container_scenarios: Optional[ContainerScenarioConfig] = Field(
        alias="container-scenarios", default=None
    )
    node_cpu_hog: Optional[NodeHogScenarioConfig] = Field(
        alias="node-cpu-hog", default=None
    )
    node_memory_hog: Optional[NodeHogScenarioConfig] = Field(
        alias="node-memory-hog", default=None
    )


class FitnessFunctionType(str, Enum):
    point = 'point'
    range = 'range'


class FitnessFunction(BaseModel):
    query: str  # PromQL
    type: FitnessFunctionType = FitnessFunctionType.point
    include_krkn_failure: bool = False


class ConfigFile(BaseModel):
    kubeconfig_file_path: str  # Path to kubeconfig

    generations: int = 20  # Total number of generations to run.
    population_size: int = 10  # Initial population size

    mutation_rate: float = const.MUTATION_RATE  # How often mutation should occur for each scenario parameter (0.0-1.0)
    crossover_rate: float = const.CROSSOVER_RATE    # How often crossover should occur for each scenario parameter (0.0-1.0)
    composition_rate: float = const.CROSSOVER_COMPOSITION_RATE  # How often a crossover would lead to composition (0.0-1.0)

    population_injection_rate: float = const.POPULATION_INJECTION_RATE  # How often a random samples gets added to new population (0.0-1.0)
    population_injection_size: int = const.POPULATION_INJECTION_SIZE    # What's the size of random samples that gets added to new population

    fitness_function: FitnessFunction

    scenario: ScenarioConfig = ScenarioConfig()
