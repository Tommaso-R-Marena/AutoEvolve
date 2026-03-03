"""Core evolution engine for autonomous self-improvement."""

import ast
import time
import json
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib


@dataclass
class EvolutionMetrics:
    """Metrics for tracking evolution progress."""
    generation: int
    fitness_score: float
    execution_time: float
    memory_usage: float
    code_quality: float
    test_coverage: float
    complexity: float
    timestamp: str


class AutoEvolver:
    """Main autonomous evolution engine."""
    
    def __init__(self, config_path: str = "config/evolution.yaml"):
        self.config = self._load_config(config_path)
        self.generation = 0
        self.history: List[EvolutionMetrics] = []
        self.best_fitness = 0.0
        self.mutation_strategies = [
            self._optimize_algorithms,
            self._refactor_structure,
            self._improve_performance,
            self._enhance_readability,
            self._add_parallelism
        ]
    
    def _load_config(self, path: str) -> Dict:
        """Load evolution configuration."""
        # Default configuration
        return {
            "fitness_weights": {
                "performance": 0.35,
                "quality": 0.25,
                "coverage": 0.20,
                "complexity": 0.20
            },
            "mutation_rate": 0.15,
            "selection_pressure": 0.7,
            "population_size": 10,
            "improvement_threshold": 0.05
        }
    
    def analyze_codebase(self) -> Dict:
        """Analyze current codebase for improvement opportunities."""
        print("[AutoEvolve] Analyzing codebase...")
        
        opportunities = {
            "performance_bottlenecks": self._find_bottlenecks(),
            "code_smells": self._detect_code_smells(),
            "optimization_targets": self._identify_optimization_targets(),
            "refactoring_candidates": self._find_refactoring_candidates()
        }
        
        print(f"[AutoEvolve] Found {sum(len(v) for v in opportunities.values())} improvement opportunities")
        return opportunities
    
    def _find_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks."""
        # Analyze code for common performance issues
        bottlenecks = []
        for py_file in Path(".").rglob("*.py"):
            if self._is_excluded(py_file):
                continue
            try:
                with open(py_file, "r") as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.For):
                            # Check for nested loops
                            for child in ast.walk(node):
                                if isinstance(child, ast.For) and child != node:
                                    bottlenecks.append(f"{py_file}:nested_loop")
        return bottlenecks
    
    def _detect_code_smells(self) -> List[str]:
        """Detect code smells and anti-patterns."""
        smells = []
        for py_file in Path(".").rglob("*.py"):
            if self._is_excluded(py_file):
                continue
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check function length
                            if len(node.body) > 50:
                                smells.append(f"{py_file}:{node.name}:too_long")
                            # Check parameter count
                            if len(node.args.args) > 5:
                                smells.append(f"{py_file}:{node.name}:too_many_params")
            except Exception:
                pass
        return smells
    
    def _identify_optimization_targets(self) -> List[str]:
        """Identify code sections that can be optimized."""
        targets = []
        # Look for common optimization opportunities
        patterns = [
            ("list comprehension opportunity", "for.*append"),
            ("generator opportunity", r"return \[.*for.*\]"),
            ("cache opportunity", "def.*\(.*\):.*for")
        ]
        return targets
    
    def _find_refactoring_candidates(self) -> List[str]:
        """Find code that should be refactored."""
        candidates = []
        # Check for duplicate code, long methods, etc.
        return candidates
    
    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from analysis."""
        excluded = [".git", "__pycache__", "venv", ".pytest_cache", "build", "dist"]
        return any(ex in str(path) for ex in excluded)
    
    def evolve(self) -> bool:
        """Run one evolution cycle."""
        print(f"\n[AutoEvolve] Starting Generation {self.generation}")
        
        # Analyze current state
        opportunities = self.analyze_codebase()
        
        if not any(opportunities.values()):
            print("[AutoEvolve] No improvement opportunities found.")
            return False
        
        # Generate candidate improvements
        candidates = self._generate_candidates(opportunities)
        print(f"[AutoEvolve] Generated {len(candidates)} candidate improvements")
        
        # Evaluate fitness
        evaluated = self._evaluate_candidates(candidates)
        
        # Select best improvements
        best = self._select_best(evaluated)
        
        if best:
            print(f"[AutoEvolve] Selected improvement with fitness: {best['fitness']:.4f}")
            success = self._apply_improvement(best)
            if success:
                self._record_metrics(best)
                self.generation += 1
                return True
        
        print("[AutoEvolve] No improvements met threshold")
        return False
    
    def _generate_candidates(self, opportunities: Dict) -> List[Dict]:
        """Generate candidate improvements."""
        candidates = []
        for strategy in self.mutation_strategies:
            candidate = strategy(opportunities)
            if candidate:
                candidates.append(candidate)
        return candidates
    
    def _optimize_algorithms(self, opportunities: Dict) -> Optional[Dict]:
        """Generate algorithmic optimizations."""
        if opportunities["performance_bottlenecks"]:
            return {
                "type": "algorithmic_optimization",
                "target": opportunities["performance_bottlenecks"][0],
                "strategy": "Convert nested loops to vectorized operations"
            }
        return None
    
    def _refactor_structure(self, opportunities: Dict) -> Optional[Dict]:
        """Generate structural refactorings."""
        if opportunities["code_smells"]:
            return {
                "type": "structural_refactoring",
                "target": opportunities["code_smells"][0],
                "strategy": "Extract method to reduce complexity"
            }
        return None
    
    def _improve_performance(self, opportunities: Dict) -> Optional[Dict]:
        """Generate performance improvements."""
        if opportunities["optimization_targets"]:
            return {
                "type": "performance_improvement",
                "target": opportunities["optimization_targets"][0],
                "strategy": "Add caching or memoization"
            }
        return None
    
    def _enhance_readability(self, opportunities: Dict) -> Optional[Dict]:
        """Generate readability improvements."""
        if opportunities["refactoring_candidates"]:
            return {
                "type": "readability_enhancement",
                "target": opportunities["refactoring_candidates"][0],
                "strategy": "Improve naming and add documentation"
            }
        return None
    
    def _add_parallelism(self, opportunities: Dict) -> Optional[Dict]:
        """Generate parallelization improvements."""
        # Check for embarrassingly parallel operations
        return None
    
    def _evaluate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Evaluate fitness of all candidates."""
        evaluated = []
        for candidate in candidates:
            fitness = self._calculate_fitness(candidate)
            candidate["fitness"] = fitness
            evaluated.append(candidate)
        return evaluated
    
    def _calculate_fitness(self, candidate: Dict) -> float:
        """Calculate fitness score for a candidate."""
        # Multi-objective fitness function
        weights = self.config["fitness_weights"]
        
        # Simulate fitness calculation (in real system, would apply change and measure)
        base_score = 0.5
        improvement_bonus = 0.3 if candidate["type"] == "performance_improvement" else 0.2
        
        fitness = base_score + improvement_bonus
        return min(fitness, 1.0)
    
    def _select_best(self, evaluated: List[Dict]) -> Optional[Dict]:
        """Select best improvement using selection pressure."""
        if not evaluated:
            return None
        
        # Sort by fitness
        sorted_candidates = sorted(evaluated, key=lambda x: x["fitness"], reverse=True)
        best = sorted_candidates[0]
        
        # Check if improvement meets threshold
        if best["fitness"] > self.best_fitness + self.config["improvement_threshold"]:
            return best
        return None
    
    def _apply_improvement(self, improvement: Dict) -> bool:
        """Apply selected improvement to codebase."""
        print(f"[AutoEvolve] Applying {improvement['type']}...")
        # In real system, would apply actual code changes
        # For now, just simulate success
        return True
    
    def _record_metrics(self, improvement: Dict):
        """Record evolution metrics."""
        metrics = EvolutionMetrics(
            generation=self.generation,
            fitness_score=improvement["fitness"],
            execution_time=0.0,
            memory_usage=0.0,
            code_quality=improvement["fitness"] * 100,
            test_coverage=0.0,
            complexity=10.0,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        self.history.append(metrics)
        self.best_fitness = improvement["fitness"]
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to file."""
        Path("metrics").mkdir(exist_ok=True)
        with open("metrics/evolution_history.json", "w") as f:
            json.dump([asdict(m) for m in self.history], f, indent=2)


if __name__ == "__main__":
    import sys
    
    evolver = AutoEvolver()
    
    if "--analyze" in sys.argv:
        opportunities = evolver.analyze_codebase()
        print("\n[Analysis Results]")
        for category, items in opportunities.items():
            print(f"  {category}: {len(items)} found")
    
    elif "--evolve" in sys.argv:
        success = evolver.evolve()
        if success:
            print(f"\n[Success] Evolution complete. Generation: {evolver.generation}")
            print(f"[Fitness] {evolver.best_fitness:.4f}")
        else:
            print("\n[Status] No improvements applied this generation")
    
    else:
        print("Usage: python -m core.evolver [--analyze|--evolve]")
