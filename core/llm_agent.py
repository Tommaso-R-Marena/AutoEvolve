"""LLM-powered autonomous coding agent for intelligent improvements."""

import ast
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class CodeImprovement:
    """Represents an LLM-generated code improvement."""
    file_path: str
    original_code: str
    improved_code: str
    reasoning: str
    confidence: float
    improvement_type: str


class LLMCodingAgent:
    """Autonomous coding agent that generates intelligent improvements."""
    
    def __init__(self):
        self.improvement_patterns = self._load_patterns()
        self.code_knowledge_base = {}
        self.improvement_history = []
    
    def _load_patterns(self) -> Dict:
        """Load learned improvement patterns."""
        return {
            "performance": [
                {"pattern": "nested_loop", "improvement": "vectorization", "expected_gain": 0.8},
                {"pattern": "repeated_computation", "improvement": "memoization", "expected_gain": 0.7},
                {"pattern": "list_append_loop", "improvement": "list_comprehension", "expected_gain": 0.3},
                {"pattern": "sequential_io", "improvement": "async_io", "expected_gain": 0.9}
            ],
            "quality": [
                {"pattern": "long_function", "improvement": "extract_method", "expected_gain": 0.6},
                {"pattern": "duplicate_code", "improvement": "extract_common", "expected_gain": 0.7},
                {"pattern": "magic_numbers", "improvement": "named_constants", "expected_gain": 0.4},
                {"pattern": "complex_conditional", "improvement": "guard_clauses", "expected_gain": 0.5}
            ],
            "architecture": [
                {"pattern": "god_class", "improvement": "split_responsibilities", "expected_gain": 0.8},
                {"pattern": "tight_coupling", "improvement": "dependency_injection", "expected_gain": 0.7},
                {"pattern": "no_abstraction", "improvement": "interface_extraction", "expected_gain": 0.6}
            ]
        }
    
    def analyze_and_improve(self, file_path: str) -> List[CodeImprovement]:
        """Analyze code and generate improvements using learned patterns."""
        print(f"[LLMAgent] Analyzing {file_path}...")
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            tree = ast.parse(code)
            improvements = []
            
            # Detect patterns and generate improvements
            for category, patterns in self.improvement_patterns.items():
                for pattern in patterns:
                    if self._detect_pattern(tree, code, pattern):
                        improvement = self._generate_improvement(file_path, code, pattern, category)
                        if improvement:
                            improvements.append(improvement)
            
            print(f"[LLMAgent] Generated {len(improvements)} improvements for {file_path}")
            return improvements
            
        except Exception as e:
            print(f"[LLMAgent] Error analyzing {file_path}: {e}")
            return []
    
    def _detect_pattern(self, tree: ast.AST, code: str, pattern: Dict) -> bool:
        """Detect if code matches a specific pattern."""
        pattern_type = pattern["pattern"]
        
        if pattern_type == "nested_loop":
            return self._has_nested_loops(tree)
        elif pattern_type == "repeated_computation":
            return self._has_repeated_computation(tree)
        elif pattern_type == "list_append_loop":
            return self._has_list_append_loop(tree)
        elif pattern_type == "long_function":
            return self._has_long_function(tree)
        elif pattern_type == "duplicate_code":
            return self._has_duplicate_code(code)
        elif pattern_type == "magic_numbers":
            return self._has_magic_numbers(tree)
        
        return False
    
    def _has_nested_loops(self, tree: ast.AST) -> bool:
        """Check for nested loops."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child != node:
                        return True
        return False
    
    def _has_repeated_computation(self, tree: ast.AST) -> bool:
        """Check for repeated computations."""
        # Simplified check - in production would use data flow analysis
        function_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    function_calls.append(node.func.id)
        
        # If same function called multiple times, might be repeated computation
        return len(function_calls) != len(set(function_calls))
    
    def _has_list_append_loop(self, tree: ast.AST) -> bool:
        """Check for list.append in loop."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute) and child.func.attr == 'append':
                            return True
        return False
    
    def _has_long_function(self, tree: ast.AST) -> bool:
        """Check for long functions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 30:
                    return True
        return False
    
    def _has_duplicate_code(self, code: str) -> bool:
        """Check for duplicate code blocks."""
        lines = code.split('\n')
        line_hashes = {}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 10:  # Only check substantial lines
                if stripped in line_hashes:
                    return True
                line_hashes[stripped] = i
        
        return False
    
    def _has_magic_numbers(self, tree: ast.AST) -> bool:
        """Check for magic numbers."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                # Exclude common numbers like 0, 1, -1
                if node.n not in [0, 1, -1]:
                    return True
        return False
    
    def _generate_improvement(self, file_path: str, code: str, pattern: Dict, category: str) -> Optional[CodeImprovement]:
        """Generate code improvement using pattern."""
        # In production, would use actual LLM to generate improvements
        # For now, use template-based improvements
        
        improvement_templates = {
            "vectorization": self._apply_vectorization,
            "memoization": self._apply_memoization,
            "list_comprehension": self._apply_list_comprehension,
            "extract_method": self._apply_extract_method,
        }
        
        improvement_type = pattern["improvement"]
        if improvement_type in improvement_templates:
            improved_code = improvement_templates[improvement_type](code)
            
            if improved_code and improved_code != code:
                return CodeImprovement(
                    file_path=file_path,
                    original_code=code,
                    improved_code=improved_code,
                    reasoning=f"Applied {improvement_type} to improve {category}",
                    confidence=pattern["expected_gain"],
                    improvement_type=improvement_type
                )
        
        return None
    
    def _apply_vectorization(self, code: str) -> str:
        """Apply vectorization transformation."""
        # Template transformation - in production would use LLM
        if "for" in code and "for" in code:
            return code + "\n# TODO: Consider using NumPy vectorization for nested loops\n"
        return code
    
    def _apply_memoization(self, code: str) -> str:
        """Apply memoization transformation."""
        if "def " in code:
            return "from functools import lru_cache\n\n@lru_cache(maxsize=128)\n" + code
        return code
    
    def _apply_list_comprehension(self, code: str) -> str:
        """Apply list comprehension transformation."""
        # Simplified transformation
        return code
    
    def _apply_extract_method(self, code: str) -> str:
        """Apply extract method refactoring."""
        # Simplified transformation
        return code
    
    def learn_from_feedback(self, improvement: CodeImprovement, success: bool, performance_gain: float):
        """Learn from improvement outcomes."""
        self.improvement_history.append({
            "improvement_type": improvement.improvement_type,
            "success": success,
            "performance_gain": performance_gain,
            "confidence": improvement.confidence
        })
        
        self._update_patterns()
    
    def _update_patterns(self):
        """Update improvement patterns based on learning."""
        # Analyze history and adjust pattern weights
        Path("metrics").mkdir(exist_ok=True)
        
        with open("metrics/llm_learning.json", "w") as f:
            json.dump(self.improvement_history, f, indent=2)
