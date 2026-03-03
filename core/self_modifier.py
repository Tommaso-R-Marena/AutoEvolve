"""Self-modification engine that can improve its own code."""

import ast
import astor
from typing import List, Dict, Optional
from pathlib import Path
import difflib
import subprocess
import json


class SelfModificationEngine:
    """Enables the system to modify its own source code safely."""
    
    def __init__(self, safety_level: str = "high"):
        self.safety_level = safety_level
        self.modification_history = []
        self.protected_functions = [
            "__init__",
            "_safety_check",
            "_rollback"
        ]
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def propose_self_modification(self, target_file: str, target_function: str, improvement: str) -> Optional[Dict]:
        """Propose a modification to the system's own code."""
        print(f"[SelfModifier] Proposing modification to {target_file}:{target_function}")
        
        # Safety check
        if not self._safety_check(target_file, target_function):
            print("[SelfModifier] Modification blocked by safety checks")
            return None
        
        try:
            # Read current code
            with open(target_file, 'r') as f:
                source_code = f.read()
            
            # Parse AST
            tree = ast.parse(source_code)
            
            # Find target function
            modified = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == target_function:
                    # Apply improvement
                    modified_node = self._apply_improvement(node, improvement)
                    if modified_node:
                        # Replace node
                        node.body = modified_node.body
                        modified = True
                        break
            
            if not modified:
                print(f"[SelfModifier] Target function {target_function} not found")
                return None
            
            # Generate modified code
            try:
                modified_code = astor.to_source(tree)
            except:
                # Fallback if astor fails
                modified_code = ast.unparse(tree)
            
            # Create proposal
            proposal = {
                "target_file": target_file,
                "target_function": target_function,
                "original_code": source_code,
                "modified_code": modified_code,
                "improvement_type": improvement,
                "diff": self._generate_diff(source_code, modified_code)
            }
            
            print("[SelfModifier] Modification proposal generated")
            return proposal
            
        except Exception as e:
            print(f"[SelfModifier] Error generating proposal: {e}")
            return None
    
    def apply_modification(self, proposal: Dict) -> bool:
        """Apply proposed modification with safety measures."""
        print(f"[SelfModifier] Applying modification to {proposal['target_file']}...")
        
        target_file = proposal['target_file']
        
        # Create backup
        backup_path = self._create_backup(target_file)
        print(f"[SelfModifier] Created backup: {backup_path}")
        
        try:
            # Write modified code
            with open(target_file, 'w') as f:
                f.write(proposal['modified_code'])
            
            # Verify syntax
            if not self._verify_syntax(target_file):
                print("[SelfModifier] Syntax verification failed - rolling back")
                self._rollback(target_file, backup_path)
                return False
            
            # Run tests
            if not self._run_tests():
                print("[SelfModifier] Tests failed - rolling back")
                self._rollback(target_file, backup_path)
                return False
            
            # Record successful modification
            self._record_modification(proposal, success=True)
            print("[SelfModifier] ✓ Modification applied successfully")
            return True
            
        except Exception as e:
            print(f"[SelfModifier] Error applying modification: {e}")
            self._rollback(target_file, backup_path)
            return False
    
    def _safety_check(self, target_file: str, target_function: str) -> bool:
        """Perform safety checks before modification."""
        # Don't modify protected functions
        if target_function in self.protected_functions:
            print(f"[SelfModifier] Function {target_function} is protected")
            return False
        
        # Don't modify if too many recent modifications
        recent_mods = [m for m in self.modification_history if m.get('success', False)]
        if len(recent_mods) > 10:
            print("[SelfModifier] Too many recent modifications - cooling down")
            return False
        
        # Check if file exists
        if not Path(target_file).exists():
            print(f"[SelfModifier] Target file {target_file} not found")
            return False
        
        return True
    
    def _apply_improvement(self, node: ast.FunctionDef, improvement: str) -> Optional[ast.FunctionDef]:
        """Apply improvement to function AST node."""
        # Template improvements - in production would use LLM
        
        if improvement == "add_caching":
            # Add caching logic
            cache_check = ast.parse("if args in _cache: return _cache[args]").body[0]
            cache_store = ast.parse("_cache[args] = result").body[0]
            
            # Insert at beginning and before return
            new_body = [cache_check] + node.body + [cache_store]
            node.body = new_body
        
        elif improvement == "add_type_hints":
            # Add type hints (simplified)
            if not node.returns:
                node.returns = ast.Name(id='Any', ctx=ast.Load())
        
        elif improvement == "optimize_loop":
            # Optimize loops (placeholder)
            pass
        
        return node
    
    def _create_backup(self, file_path: str) -> Path:
        """Create backup of file before modification."""
        import shutil
        import time
        
        timestamp = int(time.time())
        backup_name = f"{Path(file_path).stem}_{timestamp}.py"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _verify_syntax(self, file_path: str) -> bool:
        """Verify Python syntax of modified file."""
        try:
            with open(file_path, 'r') as f:
                ast.parse(f.read())
            return True
        except SyntaxError:
            return False
    
    def _run_tests(self) -> bool:
        """Run test suite to verify modification."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _rollback(self, file_path: str, backup_path: Path):
        """Rollback modification."""
        import shutil
        shutil.copy2(backup_path, file_path)
        print(f"[SelfModifier] Rolled back {file_path}")
    
    def _generate_diff(self, original: str, modified: str) -> str:
        """Generate diff between original and modified code."""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile='original',
            tofile='modified'
        )
        return ''.join(diff)
    
    def _record_modification(self, proposal: Dict, success: bool):
        """Record modification history."""
        record = {
            "target_file": proposal['target_file'],
            "target_function": proposal['target_function'],
            "improvement_type": proposal['improvement_type'],
            "success": success,
            "timestamp": str(np.datetime64('now'))
        }
        
        self.modification_history.append(record)
        
        Path("metrics").mkdir(exist_ok=True)
        with open("metrics/self_modifications.json", "w") as f:
            json.dump(self.modification_history, f, indent=2)
