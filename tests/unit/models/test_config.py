"""
ConfigFile model tests
"""

import pytest
from pydantic import ValidationError

from krkn_ai.models.config import (
    ConfigFile,
    FitnessFunction,
    FitnessFunctionType,
    FitnessFunctionItem,
    ScenarioConfig,
    HealthCheckConfig,
    HealthCheckApplicationConfig,
    OutputConfig,
    ClusterComponents,
)
from krkn_ai.models.cluster_components import Namespace, Node


class TestConfigFile:
    """Test ConfigFile model validation and default values"""

    def test_config_file_creation(self):
        """Test ConfigFile with minimal required fields and with all fields"""
        cluster = ClusterComponents(namespaces=[], nodes=[])

        # Test minimal required fields
        config_min = ConfigFile(
            kubeconfig_file_path="/path/to/kubeconfig",
            fitness_function=FitnessFunction(query="test_query"),
            cluster_components=cluster,
        )
        assert config_min.kubeconfig_file_path == "/path/to/kubeconfig"
        assert config_min.fitness_function.query == "test_query"
        assert config_min.generations == 20
        assert config_min.population_size == 10
        assert config_min.parameters == {}
        assert isinstance(config_min.scenario, ScenarioConfig)
        assert isinstance(config_min.health_checks, HealthCheckConfig)
        assert isinstance(config_min.output, OutputConfig)

        # Test with all fields
        cluster_full = ClusterComponents(
            namespaces=[Namespace(name="test-ns")], nodes=[Node(name="test-node")]
        )
        fitness = FitnessFunction(
            query="up{job='test'}",
            type=FitnessFunctionType.range,
            include_krkn_failure=False,
        )
        scenario_config = ScenarioConfig(**{"pod-scenarios": {"enable": True}})
        config = ConfigFile(
            kubeconfig_file_path="/path/to/kubeconfig",
            parameters={"key1": "value1"},
            generations=50,
            population_size=20,
            fitness_function=fitness,
            scenario=scenario_config,
            health_checks=HealthCheckConfig(
                stop_watcher_on_failure=True,
                applications=[
                    HealthCheckApplicationConfig(
                        name="app1", url="http://localhost:8080/health"
                    )
                ],
            ),
            output=OutputConfig(result_name_fmt="gen_%g_scenario_%s.yaml"),
            cluster_components=cluster_full,
        )
        assert config.generations == 50
        assert config.population_size == 20
        assert config.parameters["key1"] == "value1"
        assert config.scenario.pod_scenarios.enable is True
        assert len(config.health_checks.applications) == 1

    def test_config_missing_required_fields_raises_error(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            ConfigFile()

        with pytest.raises(ValidationError):
            ConfigFile(kubeconfig_file_path="/path/to/kubeconfig")

        with pytest.raises(ValidationError):
            ConfigFile(
                kubeconfig_file_path="/path/to/kubeconfig",
                fitness_function=FitnessFunction(query="test"),
            )


class TestFitnessFunction:
    """Test FitnessFunction model validation"""

    def test_fitness_function_creation(self):
        """Test FitnessFunction with query field and with items list"""
        # Test with query field
        fitness_query = FitnessFunction(
            query="up{job='test'}", type=FitnessFunctionType.point
        )
        assert fitness_query.query == "up{job='test'}"
        assert fitness_query.type == FitnessFunctionType.point
        assert fitness_query.include_krkn_failure is True
        assert fitness_query.items == []

        # Test with items list
        fitness_items = FitnessFunction(
            items=[
                FitnessFunctionItem(
                    query="cpu_usage", type=FitnessFunctionType.range, weight=0.5
                ),
                FitnessFunctionItem(query="memory_usage", weight=0.3),
            ]
        )
        assert len(fitness_items.items) == 2
        assert fitness_items.items[0].query == "cpu_usage"
        assert fitness_items.items[0].weight == 0.5

    def test_fitness_function_requires_query_or_items(self):
        """Test that FitnessFunction requires at least query or items"""
        with pytest.raises(ValidationError, match="at least one fitness function"):
            FitnessFunction()

    def test_fitness_function_item_weight_validation(self):
        """Test FitnessFunctionItem weight must be between 0 and 1"""
        # Valid weights
        item1 = FitnessFunctionItem(query="test", weight=0.0)
        item2 = FitnessFunctionItem(query="test", weight=1.0)
        item3 = FitnessFunctionItem(query="test", weight=0.5)
        assert item1.weight == 0.0
        assert item2.weight == 1.0
        assert item3.weight == 0.5

        # Invalid weights
        with pytest.raises(ValidationError, match="outside the range"):
            FitnessFunctionItem(query="test", weight=-0.1)

        with pytest.raises(ValidationError, match="outside the range"):
            FitnessFunctionItem(query="test", weight=1.1)

    def test_fitness_function_item_auto_id(self):
        """Test that FitnessFunctionItem gets auto-incremented IDs"""
        item1 = FitnessFunctionItem(query="test1")
        item2 = FitnessFunctionItem(query="test2")
        item3 = FitnessFunctionItem(query="test3")
        assert item1.id < item2.id < item3.id


class TestHealthCheckConfig:
    """Test HealthCheckConfig model"""

    def test_health_check_config_creation(self):
        """Test HealthCheckConfig and HealthCheckApplicationConfig with defaults and custom values"""
        # Test HealthCheckConfig defaults
        config = HealthCheckConfig()
        assert config.stop_watcher_on_failure is False
        assert config.applications == []

        # Test HealthCheckApplicationConfig with defaults and custom values
        app = HealthCheckApplicationConfig(
            name="test-app", url="http://localhost:8080/health"
        )
        assert app.name == "test-app"
        assert app.url == "http://localhost:8080/health"
        assert app.status_code == 200
        assert app.timeout == 4
        assert app.interval == 2


class TestOutputConfig:
    """Test OutputConfig model"""

    def test_output_config_creation(self):
        """Test OutputConfig with default and custom format strings"""
        # Test default format strings
        config_default = OutputConfig()
        assert config_default.result_name_fmt == "scenario_%s.yaml"
        assert config_default.graph_name_fmt == "scenario_%s.png"
        assert config_default.log_name_fmt == "scenario_%s.log"

        # Test custom format strings
        config = OutputConfig(
            result_name_fmt="gen_%g_scenario_%s.yaml",
            graph_name_fmt="gen_%g_scenario_%s.png",
            log_name_fmt="gen_%g_scenario_%s.log",
        )
        assert "%g" in config.result_name_fmt
        assert "%s" in config.result_name_fmt
