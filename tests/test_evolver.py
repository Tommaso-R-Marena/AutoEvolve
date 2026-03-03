"""Tests for the evolution engine."""

import pytest
from core.evolver import AutoEvolver, EvolutionMetrics


class TestAutoEvolver:
    """Test suite for AutoEvolver."""
    
    def test_initialization(self):
        """Test evolver initialization."""
        evolver = AutoEvolver()
        assert evolver.generation == 0
        assert evolver.best_fitness == 0.0
        assert len(evolver.history) == 0
    
    def test_config_loading(self):
        """Test configuration loading."""
        evolver = AutoEvolver()
        assert "fitness_weights" in evolver.config
        assert "mutation_rate" in evolver.config
        assert "selection_pressure" in evolver.config
    
    def test_analyze_codebase(self):
        """Test codebase analysis."""
        evolver = AutoEvolver()
        opportunities = evolver.analyze_codebase()
        
        assert "performance_bottlenecks" in opportunities
        assert "code_smells" in opportunities
        assert "optimization_targets" in opportunities
        assert "refactoring_candidates" in opportunities
    
    def test_fitness_calculation(self):
        """Test fitness score calculation."""
        evolver = AutoEvolver()
        candidate = {
            "type": "performance_improvement",
            "target": "test_target",
            "strategy": "test_strategy"
        }
        
        fitness = evolver._calculate_fitness(candidate)
        assert 0.0 <= fitness <= 1.0
    
    def test_evolution_metrics(self):
        """Test evolution metrics creation."""
        metrics = EvolutionMetrics(
            generation=1,
            fitness_score=0.75,
            execution_time=1.5,
            memory_usage=100.0,
            code_quality=85.0,
            test_coverage=80.0,
            complexity=8.0,
            timestamp="2026-03-03 00:00:00"
        )
        
        assert metrics.generation == 1
        assert metrics.fitness_score == 0.75
        assert metrics.code_quality == 85.0
