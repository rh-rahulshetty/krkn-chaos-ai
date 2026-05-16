"""
GeneticAlgorithm core functionality tests
"""

import pytest
from unittest.mock import Mock, patch

from krkn_ai.algorithm.genetic import GeneticAlgorithm
from krkn_ai.models.custom_errors import PopulationSizeError


class TestGeneticAlgorithmInitialization:
    """Test GeneticAlgorithm initialization"""

    def test_init_with_valid_config(self, minimal_config, temp_output_dir):
        """Test initialization with valid config and config file creation"""
        with patch("krkn_ai.algorithm.genetic.KrknRunner"):
            with patch(
                "krkn_ai.algorithm.genetic.ScenarioFactory.generate_valid_scenarios"
            ) as mock_gen:
                mock_gen.return_value = [("pod_scenarios", Mock)]
                run_uuid = "test-run-uuid"
                ga = GeneticAlgorithm(
                    config=minimal_config,
                    output_dir=temp_output_dir,
                    format="yaml",
                    run_uuid=run_uuid,
                )
                assert ga.config == minimal_config
                assert ga.output_dir == temp_output_dir
                assert ga.run_uuid == run_uuid
                assert ga.format == "yaml"
                assert ga.population == []
                assert len(ga.best_of_generation) == 0

    def test_init_generates_unique_run_uuid(self, minimal_config, temp_output_dir):
        """Test initialization generates a unique run UUID per instance"""
        with patch("krkn_ai.algorithm.genetic.KrknRunner"):
            with patch(
                "krkn_ai.algorithm.genetic.ScenarioFactory.generate_valid_scenarios"
            ) as mock_gen:
                mock_gen.return_value = [("pod_scenarios", Mock)]
                first = GeneticAlgorithm(
                    config=minimal_config, output_dir=temp_output_dir, format="yaml"
                )
                second = GeneticAlgorithm(
                    config=minimal_config, output_dir=temp_output_dir, format="yaml"
                )

                assert first.run_uuid != second.run_uuid

    def test_init_with_population_size_less_than_2(
        self, minimal_config, temp_output_dir
    ):
        """Test raises error when population size is less than 2"""
        minimal_config.population_size = 1
        with patch("krkn_ai.algorithm.genetic.KrknRunner"):
            with patch(
                "krkn_ai.algorithm.genetic.ScenarioFactory.generate_valid_scenarios"
            ) as mock_gen:
                mock_gen.return_value = [("pod_scenarios", Mock)]
                with pytest.raises(
                    PopulationSizeError, match="Population size should be at least 2"
                ):
                    GeneticAlgorithm(
                        config=minimal_config, output_dir=temp_output_dir, format="yaml"
                    )

    def test_init_with_odd_population_size(self, minimal_config, temp_output_dir):
        """Test odd population size is adjusted to even"""
        minimal_config.population_size = 5
        with patch("krkn_ai.algorithm.genetic.KrknRunner"):
            with patch(
                "krkn_ai.algorithm.genetic.ScenarioFactory.generate_valid_scenarios"
            ) as mock_gen:
                mock_gen.return_value = [("pod_scenarios", Mock)]
                ga = GeneticAlgorithm(
                    config=minimal_config, output_dir=temp_output_dir, format="yaml"
                )
                assert ga.config.population_size == 6


class TestGeneticAlgorithmCoreMethods:
    """Test GeneticAlgorithm core methods"""

    def test_simulate_updates_completed_generations(self, genetic_algorithm):
        """Track completed generations after simulate evaluates populations."""
        genetic_algorithm.config.generations = 2
        genetic_algorithm.config.population_size = 2
        genetic_algorithm.config.baseline.enable = False
        genetic_algorithm.config.population_injection_rate = 0.0

        first_generation = [Mock(name="scenario-1"), Mock(name="scenario-2")]
        offspring_generation = [Mock(name="scenario-3"), Mock(name="scenario-4")]

        generation_results = []
        for score in [10.0, 20.0, 30.0, 40.0]:
            result = Mock()
            result.fitness_result.fitness_score = score
            generation_results.append(result)

        with patch.object(genetic_algorithm, "run_baseline") as mock_baseline:
            with patch.object(
                genetic_algorithm, "create_population", return_value=first_generation
            ):
                with patch.object(
                    genetic_algorithm,
                    "calculate_fitness",
                    side_effect=generation_results,
                ) as mock_calculate:
                    with patch.object(
                        genetic_algorithm,
                        "select_parents",
                        return_value=(first_generation[0], first_generation[1]),
                    ):
                        with patch.object(
                            genetic_algorithm,
                            "crossover",
                            return_value=(
                                offspring_generation[0],
                                offspring_generation[1],
                            ),
                        ):
                            with patch.object(
                                genetic_algorithm,
                                "mutate",
                                side_effect=lambda scenario: scenario,
                            ):
                                genetic_algorithm.simulate()

        assert genetic_algorithm.completed_generations == 2
        assert len(genetic_algorithm.best_of_generation) == 2
        assert mock_calculate.call_count == 4
        mock_baseline.assert_called_once()

    def test_save_method_calls_reporters(self, genetic_algorithm):
        """Test save method calls all reporters"""
        with patch.object(
            genetic_algorithm.generations_reporter, "save_best_generations"
        ) as mock_save_gen:
            with patch.object(
                genetic_algorithm.generations_reporter, "save_best_generation_graph"
            ) as mock_graph:
                with patch.object(
                    genetic_algorithm.health_check_reporter, "save_report"
                ) as mock_save_report:
                    with patch.object(
                        genetic_algorithm.health_check_reporter,
                        "sort_fitness_result_csv",
                    ) as mock_sort:
                        with patch(
                            "krkn_ai.algorithm.genetic.JSONSummaryReporter"
                        ) as mock_summary_reporter:
                            mock_reporter_instance = Mock()
                            mock_summary_reporter.return_value = mock_reporter_instance
                            genetic_algorithm.best_of_generation = [Mock()]
                            genetic_algorithm.seen_population = {Mock(): Mock()}
                            final_rate = 0.42
                            genetic_algorithm.current_scenario_mutation_rate = (
                                final_rate
                            )
                            genetic_algorithm.completed_generations = 2
                            genetic_algorithm.save()

                            assert mock_save_gen.called
                            assert mock_graph.called
                            assert mock_save_report.called
                            assert mock_sort.called
                            assert mock_summary_reporter.called
                            assert (
                                mock_summary_reporter.call_args.kwargs[
                                    "scenario_mutation_rate"
                                ]
                                == final_rate
                            )
                            assert (
                                mock_summary_reporter.call_args.kwargs[
                                    "completed_generations"
                                ]
                                == 2
                            )
                            assert mock_reporter_instance.save.called
