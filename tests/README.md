<!-- Portions of this documentation were reviewed and enhanced with the assistance of AI tools (Cursor AI). -->

# Testing Guide

This document provides comprehensive guidance for running and understanding the test suite for the Krkn-AI project.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing New Tests](#writing-new-tests)
- [Test Fixtures](#test-fixtures)

## Overview

The Krkn-AI test suite is designed to provide comprehensive coverage of core functionality while remaining maintainable and fast. The tests focus on:

- **Core genetic algorithm operations**: initialization, population creation, fitness calculation, selection, crossover, mutation, composition
- **Data models**: ConfigFile, ClusterComponents, AppContext, CommandRunResult, scenario classes
- **Scenario factory**: scenario listing, generation, validation
- **Utilities**: ClusterManager (Kubernetes discovery), Prometheus client
- **Reporters**: GenerationsReporter (YAML/JSON/Graph), HealthCheckReporter (CSV/Plots)
- **Chaos engines**: KrknRunner (CLI/Hub runner), HealthCheckWatcher (threading, aggregation)
- **CLI commands**: run command (config validation, error handling), discover command (component discovery)

## Test Structure

The test suite follows a hierarchical structure that mirrors the main codebase:

```
tests/
├── __init__.py
├── conftest.py                         # Shared fixtures and configuration
├── README.md                           # This file
└── unit/                               # Unit tests
    ├── __init__.py
    │
    ├── algorithm/                      # Genetic algorithm module tests (core)
    │   ├── __init__.py
    │   ├── test_genetic_algorithm.py   # Core GeneticAlgorithm behavior
    │   ├── test_population_creation.py # Population creation
    │   ├── test_fitness_calculation.py # Fitness calculation
    │   ├── test_selection.py           # Parent selection
    │   ├── test_crossover.py           # Crossover operations
    │   ├── test_mutation.py            # Mutation operations
    │   └── test_composition.py         # Composite scenarios
    │
    ├── models/                         # Data model tests
    │   ├── __init__.py
    │   ├── test_config.py              # ConfigFile model
    │   ├── test_cluster_components.py  # ClusterComponents model
    │   ├── test_app.py                 # AppContext & CommandRunResult
    │   └── scenario/                   # Scenario model tests
    │       ├── __init__.py
    │       ├── test_base_scenario.py   # BaseScenario & CompositeScenario
    │       ├── test_scenario_factory.py # ScenarioFactory
    │       └── test_scenario_classes.py # All scenario classes
    │
    ├── utils/                          # Utility class tests
    │   ├── __init__.py
    │   ├── test_cluster_manager.py     # ClusterManager
    │   └── test_prometheus.py          # Prometheus client
    │
    ├── reporter/                       # Report generator tests
    │   ├── __init__.py
    │   ├── test_generations_reporter.py   # GenerationsReporter
    │   └── test_health_check_reporter.py  # HealthCheckReporter
    │
    ├── chaos_engines/                  # Chaos engine tests
    │   ├── __init__.py
    │   ├── test_krkn_runner.py         # KrknRunner core functionality
    │   └── test_health_check_watcher.py # HealthCheckWatcher
    │
    └── cli/                            # CLI tests
        ├── __init__.py
        └── test_cmd.py                 # CLI command tests
```

## Running Tests

### Run All Tests

To run the entire test suite:

```bash
pytest tests/
```

Or simply:

```bash
pytest
```

### Run Specific Test Modules

Run tests for a specific module:

```bash
# Algorithm tests
pytest tests/unit/algorithm/

# Model tests
pytest tests/unit/models/

# Scenario tests
pytest tests/unit/models/scenario/

# Utility tests
pytest tests/unit/utils/

# Reporter tests
pytest tests/unit/reporter/

# Chaos engine tests
pytest tests/unit/chaos_engines/

# CLI tests
pytest tests/unit/cli/
```

### Run Specific Test Files

Run a single test file:

```bash
pytest tests/unit/algorithm/test_genetic_algorithm.py
```

### Run Specific Test Functions

Run a specific test function or class:

```bash
# Run a specific test function
pytest tests/unit/algorithm/test_genetic_algorithm.py::test_init_with_valid_config

# Run all tests in a class
pytest tests/unit/algorithm/test_genetic_algorithm.py::TestGeneticAlgorithmInitialization
```

### Verbose Output

For detailed output:

```bash
pytest -v
```

For even more detail (including print statements):

```bash
pytest -vv -s
```


## Writing New Tests

### Test Naming Conventions

Follow these conventions for consistency:

- **Test files**: `test_<module_name>.py`
- **Test classes**: `Test<ClassName><Functionality>`
- **Test functions**: `test_<what_is_being_tested>`

Example:

```python
class TestGeneticAlgorithmInitialization:
    def test_init_with_valid_config(self, minimal_config, temp_output_dir):
        """Test initialization with valid config"""
        # Test implementation
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_example_function(self, fixture):
    """Test description"""
    # Arrange: Set up test data and mocks
    input_data = "test"

    # Act: Call the function being tested
    result = example_function(input_data)

    # Assert: Verify the results
    assert result == expected_output
```

### Using Fixtures

Leverage existing fixtures from `conftest.py`:

```python
def test_with_fixtures(self, minimal_config, temp_output_dir, mock_cluster_components):
    """Test using shared fixtures"""
    # Use fixtures in your test
    assert minimal_config.population_size == 4
```

### Mocking External Dependencies

Use mocking for external dependencies (Kubernetes API, file system, etc.):

```python
from unittest.mock import Mock, patch

def test_with_mocking(self):
    """Test with mocked dependencies"""
    with patch('krkn_ai.utils.cluster_manager.config.load_kube_config'):
        with patch('krkn_ai.utils.cluster_manager.client') as mock_client:
            mock_client.CoreV1Api.return_value.list_namespace.return_value = Mock()
            # Test implementation
```

### Testing Exceptions

Test that exceptions are raised correctly:

```python
import pytest
from krkn_ai.models.custom_errors import PopulationSizeError

def test_invalid_population_size(self, minimal_config):
    """Test raises error for invalid population size"""
    minimal_config.population_size = 1
    with pytest.raises(PopulationSizeError, match="Population size should be at least 2"):
        GeneticAlgorithm(config=minimal_config)
```

### Parametrized Tests

Use parametrization to test multiple scenarios:

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(self, input, expected):
    """Test multiplication with different inputs"""
    assert multiply_by_two(input) == expected
```

## Test Fixtures

The `conftest.py` file provides shared fixtures used across the test suite.

### Creating Custom Fixtures

Add new fixtures to `conftest.py` for reusability:

```python
@pytest.fixture
def custom_fixture():
    """Description of the fixture"""
    # Setup
    data = create_test_data()

    yield data

    # Teardown (optional)
    cleanup_test_data(data)
```

## Best Practices

### Test Philosophy

The test suite follows these principles:

1. **Focus on core functionality**: Test the most critical and complex logic first
2. **Avoid testing implementation details**: Test behavior, not internal structure
3. **Keep tests independent**: Each test should run in isolation
4. **Use meaningful names**: Test names should clearly describe what they test
5. **Mock external dependencies**: Don't rely on external services in unit tests
6. **Balance coverage and maintainability**: Aim for high coverage on critical paths without making tests brittle


### Contributing

When contributing new features to Krkn-AI:

1. **Develop the feature first**
2. **Run the existing test suite**: `pytest tests/` and ensure existing tests pass; if your changes break tests, fix the tests or your implementation as appropriate
3. **Add new or updated tests** for your feature to ensure correct behavior and coverage
4. **Check coverage**: Aim for >80% coverage on new code
5. **Follow naming conventions**: Use consistent naming patterns
6. **Update fixtures**: Add reusable fixtures to `conftest.py`, if needed
7. **Document complex tests**: Add clear docstrings


## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Krkn-AI Main Documentation](../README.md)
- [Original Test PR #62](https://github.com/krkn-chaos/krkn-ai/pull/62)
