"""Meta-learning optimizer that improves the evolution process itself."""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import time


@dataclass
class MetaParameters:
    """Parameters that control the evolution process."""
    mutation_rate: float
    selection_pressure: float
    population_size: int
    crossover_rate: float
    elite_fraction: float
    exploration_bonus: float


class MetaOptimizer:
    """Optimizes the optimization process itself using meta-learning."""
    
    def __init__(self):
        self.meta_params = MetaParameters(
            mutation_rate=0.15,
            selection_pressure=0.7,
            population_size=20,
            crossover_rate=0.8,
            elite_fraction=0.2,
            exploration_bonus=0.1
        )
        self.performance_history = []
        self.param_history = []
        self.meta_generation = 0
    
    def optimize_hyperparameters(self, evolution_results: List[Dict]) -> MetaParameters:
        """Optimize evolution hyperparameters based on results."""
        print("[MetaOptimizer] Optimizing evolution hyperparameters...")
        
        if len(evolution_results) < 5:
            print("[MetaOptimizer] Insufficient data for meta-optimization")
            return self.meta_params
        
        # Analyze performance trends
        recent_performance = [r.get('fitness', 0.0) for r in evolution_results[-10:]]
        avg_performance = np.mean(recent_performance)
        performance_trend = np.polyfit(range(len(recent_performance)), recent_performance, 1)[0]
        
        print(f"[MetaOptimizer] Average performance: {avg_performance:.4f}")
        print(f"[MetaOptimizer] Performance trend: {performance_trend:.6f}")
        
        # Adjust parameters based on performance
        if performance_trend < 0.001:  # Stagnating
            print("[MetaOptimizer] Detected stagnation - increasing exploration")
            self.meta_params.mutation_rate = min(0.3, self.meta_params.mutation_rate * 1.2)
            self.meta_params.exploration_bonus *= 1.5
            self.meta_params.population_size = int(self.meta_params.population_size * 1.2)
        
        elif performance_trend > 0.01:  # Improving rapidly
            print("[MetaOptimizer] Rapid improvement - intensifying exploitation")
            self.meta_params.selection_pressure = min(0.95, self.meta_params.selection_pressure * 1.1)
            self.meta_params.elite_fraction = min(0.3, self.meta_params.elite_fraction * 1.1)
        
        else:  # Steady improvement
            print("[MetaOptimizer] Steady improvement - maintaining balance")
            # Keep current parameters with minor adjustments
            self.meta_params.mutation_rate *= 0.95
        
        self._record_meta_state(avg_performance, performance_trend)
        self.meta_generation += 1
        
        return self.meta_params
    
    def adaptive_strategy_selection(self, available_strategies: List[str], history: List[Dict]) -> List[Tuple[str, float]]:
        """Adaptively select which evolution strategies to use."""
        print("[MetaOptimizer] Selecting adaptive strategies...")
        
        if not history:
            # Equal weights initially
            weights = [1.0 / len(available_strategies)] * len(available_strategies)
            return list(zip(available_strategies, weights))
        
        # Calculate success rate for each strategy
        strategy_performance = {s: [] for s in available_strategies}
        
        for entry in history:
            strategy = entry.get('strategy', '')
            success = entry.get('success', False)
            gain = entry.get('performance_gain', 0.0)
            
            if strategy in strategy_performance:
                strategy_performance[strategy].append(gain if success else 0.0)
        
        # Compute weights using softmax with temperature
        temperature = 0.5
        weights = []
        
        for strategy in available_strategies:
            if strategy_performance[strategy]:
                avg_gain = np.mean(strategy_performance[strategy])
            else:
                avg_gain = 0.1  # Small prior for untested strategies
            weights.append(avg_gain)
        
        # Apply softmax
        weights = np.array(weights)
        weights = np.exp(weights / temperature)
        weights = weights / np.sum(weights)
        
        strategy_weights = list(zip(available_strategies, weights))
        
        print("[MetaOptimizer] Strategy weights:")
        for strategy, weight in strategy_weights:
            print(f"  {strategy}: {weight:.3f}")
        
        return strategy_weights
    
    def predict_improvement_potential(self, code_features: Dict) -> float:
        """Predict potential improvement using meta-learned model."""
        # Features: complexity, size, test coverage, etc.
        complexity = code_features.get('complexity', 10.0)
        size = code_features.get('lines_of_code', 100)
        coverage = code_features.get('test_coverage', 0.5)
        
        # Simple heuristic model (in production would use trained ML model)
        potential = 0.0
        
        # High complexity = high improvement potential
        if complexity > 15:
            potential += 0.3
        
        # Large code = more room for optimization
        if size > 200:
            potential += 0.2
        
        # Low coverage = potential for test improvements
        if coverage < 0.7:
            potential += 0.2
        
        # Add some exploration bonus
        potential += self.meta_params.exploration_bonus
        
        return min(1.0, potential)
    
    def self_modification_decision(self, current_performance: float, risk_tolerance: float = 0.3) -> bool:
        """Decide whether to allow self-modification of core evolution code."""
        print("[MetaOptimizer] Evaluating self-modification decision...")
        
        if len(self.performance_history) < 10:
            print("[MetaOptimizer] Insufficient history for safe self-modification")
            return False
        
        # Check if performance is above threshold
        recent_avg = np.mean(self.performance_history[-5:])
        overall_avg = np.mean(self.performance_history)
        
        if recent_avg < overall_avg * 0.8:
            print("[MetaOptimizer] Performance below threshold - blocking self-modification")
            return False
        
        # Check for stability
        recent_std = np.std(self.performance_history[-10:])
        
        if recent_std > risk_tolerance:
            print("[MetaOptimizer] High variance detected - self-modification risky")
            return False
        
        # Conditions met for self-modification
        print("[MetaOptimizer] ✓ Safe to proceed with self-modification")
        return True
    
    def generate_meta_improvement(self) -> Optional[Dict]:
        """Generate improvements to the evolution system itself."""
        print("[MetaOptimizer] Generating meta-level improvements...")
        
        improvements = []
        
        # Suggest new mutation operators
        if self.meta_generation > 5:
            improvements.append({
                "type": "new_operator",
                "operator": "gradient_guided_mutation",
                "rationale": "Combine evolutionary and gradient-based approaches",
                "priority": 0.8
            })
        
        # Suggest fitness function modifications
        if len(self.performance_history) > 20:
            improvements.append({
                "type": "fitness_refinement",
                "modification": "Add adaptive weights based on current bottlenecks",
                "rationale": "Dynamic fitness functions adapt to changing needs",
                "priority": 0.9
            })
        
        # Suggest architecture changes
        improvements.append({
            "type": "architecture",
            "modification": "Implement multi-objective Pareto optimization",
            "rationale": "Better handle competing objectives",
            "priority": 0.7
        })
        
        if improvements:
            best_improvement = max(improvements, key=lambda x: x['priority'])
            print(f"[MetaOptimizer] Suggested: {best_improvement['type']} - {best_improvement['modification']}")
            return best_improvement
        
        return None
    
    def _record_meta_state(self, performance: float, trend: float):
        """Record meta-optimization state."""
        self.performance_history.append(performance)
        self.param_history.append(asdict(self.meta_params))
        
        Path("metrics").mkdir(exist_ok=True)
        
        with open("metrics/meta_optimization.json", "w") as f:
            json.dump({
                "generation": self.meta_generation,
                "performance_history": self.performance_history,
                "current_params": asdict(self.meta_params),
                "trend": trend
            }, f, indent=2)
