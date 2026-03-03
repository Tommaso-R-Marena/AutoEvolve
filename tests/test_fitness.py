"""Tests for fitness evaluators."""

import pytest
from core.fitness import FitnessEvaluator, FitnessScore


class TestFitnessEvaluator:
    """Test suite for FitnessEvaluator."""
    
    def test_initialization(self):
        """Test evaluator initialization."""
        evaluator = FitnessEvaluator()
        assert "performance" in evaluator.weights
        assert "quality" in evaluator.weights
        assert "coverage" in evaluator.weights
        assert "complexity" in evaluator.weights
    
    def test_custom_weights(self):
        """Test custom weight configuration."""
        weights = {
            "performance": 0.5,
            "quality": 0.2,
            "coverage": 0.2,
            "complexity": 0.1
        }
        evaluator = FitnessEvaluator(weights)
        assert evaluator.weights["performance"] == 0.5
    
    def test_evaluate(self):
        """Test fitness evaluation."""
        evaluator = FitnessEvaluator()
        score = evaluator.evaluate()
        
        assert isinstance(score, FitnessScore)
        assert 0.0 <= score.performance <= 1.0
        assert 0.0 <= score.quality <= 1.0
        assert 0.0 <= score.coverage <= 1.0
        assert 0.0 <= score.complexity <= 1.0
        assert 0.0 <= score.overall <= 1.0
    
    def test_compare_scores(self):
        """Test score comparison."""
        evaluator = FitnessEvaluator()
        
        before = FitnessScore(0.5, 0.6, 0.4, 0.7, 0.55)
        after = FitnessScore(0.7, 0.7, 0.5, 0.8, 0.70)
        
        improvements = evaluator.compare(before, after)
        
        assert improvements["performance"] == 0.2
        assert improvements["quality"] == 0.1
        assert improvements["overall"] == 0.15
