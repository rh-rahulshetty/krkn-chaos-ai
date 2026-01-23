"""
Composition operation tests
"""

from krkn_ai.models.scenario.base import CompositeScenario, CompositeDependency
from krkn_ai.models.scenario.scenario_dummy import DummyScenario
from krkn_ai.models.cluster_components import ClusterComponents


class TestComposition:
    """Test composition functionality"""

    def test_composition_creates_composite_scenario(self, genetic_algorithm):
        """Test that composition creates a composite scenario with valid dependency"""
        scenario_a = DummyScenario(cluster_components=ClusterComponents())
        scenario_b = DummyScenario(cluster_components=ClusterComponents())

        composite = genetic_algorithm.composition(scenario_a, scenario_b)

        # Should create a CompositeScenario
        assert isinstance(composite, CompositeScenario)
        assert composite.scenario_a == scenario_a
        assert composite.scenario_b == scenario_b
        # Dependency should be one of the valid enum values
        assert composite.dependency in CompositeDependency
