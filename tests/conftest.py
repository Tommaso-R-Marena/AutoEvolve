"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
from pathlib import Path
import json


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_code():
    """Provide sample code for testing."""
    return '''
def example_function(x, y):
    return x + y

class ExampleClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value
'''


@pytest.fixture
def sample_evolution_config():
    """Provide sample evolution configuration."""
    return {
        "fitness_weights": {
            "performance": 0.35,
            "quality": 0.25,
            "coverage": 0.20,
            "complexity": 0.20
        },
        "mutation_rate": 0.15,
        "selection_pressure": 0.7,
        "population_size": 10
    }


@pytest.fixture
def mock_fitness_function():
    """Provide a mock fitness function."""
    def fitness(individual):
        return 0.75  # Mock fitness score
    return fitness


@pytest.fixture(autouse=True)
def cleanup_metrics(tmp_path):
    """Clean up metrics directory after tests."""
    yield
    # Cleanup can be added here if needed


@pytest.fixture
def sample_code_variant():
    """Provide a sample code variant for testing."""
    return {
        'code': 'def test(): return True',
        'fitness': 0.0,
        'strategy': 'test_strategy'
    }
