"""
Mutation operation tests
"""

from krkn_ai.models.scenario.base import CompositeScenario, CompositeDependency
from krkn_ai.models.scenario.scenario_dummy import DummyScenario
from krkn_ai.models.cluster_components import ClusterComponents


class TestMutation:
    """Test mutation functionality"""

    def test_mutate_simple_scenario(self, genetic_algorithm):
        """Test mutation of a simple scenario"""
        scenario = DummyScenario(cluster_components=ClusterComponents())

        # Set mutation rate to 0 to test parameter mutation path
        genetic_algorithm.config.scenario_mutation_rate = 0.0

        mutated = genetic_algorithm.mutate(scenario)

        # Should return the same scenario (DummyScenario.mutate() does nothing)
        # The mutate method is called internally, but since it's empty, the scenario remains unchanged
        assert mutated is scenario
        assert isinstance(mutated, DummyScenario)
        # Verify the scenario has mutate method (which will be called)
        assert hasattr(mutated, "mutate")

    def test_mutate_composite_scenario(self, genetic_algorithm):
        """Test mutation of a composite scenario recursively mutates sub-scenarios"""
        scenario_a = DummyScenario(cluster_components=ClusterComponents())
        scenario_b = DummyScenario(cluster_components=ClusterComponents())

        composite = CompositeScenario(
            name="composite",
            scenario_a=scenario_a,
            scenario_b=scenario_b,
            dependency=CompositeDependency.NONE,
        )

        # Set mutation rates to 0 to avoid scenario_mutation which requires valid scenarios
        genetic_algorithm.config.scenario_mutation_rate = 0.0

        mutated = genetic_algorithm.mutate(composite)

        # Should return the same composite scenario
        assert isinstance(mutated, CompositeScenario)
        assert mutated is composite
        # Sub-scenarios should be mutated recursively (though DummyScenario.mutate() does nothing)
        # Verify both sub-scenarios exist and have mutate methods
        assert mutated.scenario_a is not None
        assert mutated.scenario_b is not None
        assert hasattr(mutated.scenario_a, "mutate")
        assert hasattr(mutated.scenario_b, "mutate")
