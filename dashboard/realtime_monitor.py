"""Real-time monitoring dashboard for evolution system."""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sys


@dataclass
class SystemMetrics:
    """Real-time system metrics."""
    timestamp: float
    generation: int
    fitness_score: float
    evolution_rate: float
    active_agents: int
    cpu_usage: float
    memory_usage: float
    improvement_rate: float


class RealtimeMonitor:
    """Real-time monitoring and visualization system."""
    
    def __init__(self, refresh_interval: float = 1.0):
        self.refresh_interval = refresh_interval
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Dict] = []
        self.thresholds = {
            "fitness_drop": 0.1,
            "evolution_stagnation": 5,
            "cpu_high": 90.0,
            "memory_high": 90.0
        }
        
        print("[RealtimeMonitor] Initialized real-time monitoring system")
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # Load latest evolution data
        evolution_data = self._load_latest_evolution_data()
        
        # Get system resources
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
        except ImportError:
            cpu_usage = 0.0
            memory_usage = 0.0
        
        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate()
        
        metrics = SystemMetrics(
            timestamp=time.time(),
            generation=evolution_data.get("generation", 0),
            fitness_score=evolution_data.get("fitness", 0.0),
            evolution_rate=evolution_data.get("rate", 0.0),
            active_agents=evolution_data.get("agents", 0),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            improvement_rate=improvement_rate
        )
        
        self.metrics_history.append(metrics)
        
        # Check for alerts
        self._check_alerts(metrics)
        
        return metrics
    
    def _load_latest_evolution_data(self) -> Dict:
        """Load latest evolution data."""
        history_file = Path("metrics/evolution_history.json")
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                if history:
                    latest = history[-1]
                    return {
                        "generation": latest.get("generation", 0),
                        "fitness": latest.get("fitness_score", 0.0),
                        "rate": 0.0,
                        "agents": 7
                    }
            except Exception:
                pass
        
        return {"generation": 0, "fitness": 0.0, "rate": 0.0, "agents": 0}
    
    def _calculate_improvement_rate(self) -> float:
        """Calculate rate of improvement."""
        if len(self.metrics_history) < 2:
            return 0.0
        
        recent = self.metrics_history[-10:]
        if len(recent) < 2:
            return 0.0
        
        fitness_changes = [
            recent[i].fitness_score - recent[i-1].fitness_score
            for i in range(1, len(recent))
        ]
        
        return sum(fitness_changes) / len(fitness_changes) if fitness_changes else 0.0
    
    def _check_alerts(self, metrics: SystemMetrics):
        """Check for alert conditions."""
        # Fitness drop alert
        if len(self.metrics_history) >= 2:
            prev_fitness = self.metrics_history[-2].fitness_score
            if metrics.fitness_score < prev_fitness - self.thresholds["fitness_drop"]:
                self._create_alert("fitness_drop", f"Fitness dropped from {prev_fitness:.3f} to {metrics.fitness_score:.3f}")
        
        # Evolution stagnation
        if metrics.improvement_rate < 0.001 and metrics.generation > self.thresholds["evolution_stagnation"]:
            self._create_alert("stagnation", f"Evolution stagnating at generation {metrics.generation}")
        
        # Resource alerts
        if metrics.cpu_usage > self.thresholds["cpu_high"]:
            self._create_alert("high_cpu", f"CPU usage at {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > self.thresholds["memory_high"]:
            self._create_alert("high_memory", f"Memory usage at {metrics.memory_usage:.1f}%")
    
    def _create_alert(self, alert_type: str, message: str):
        """Create system alert."""
        alert = {
            "timestamp": time.time(),
            "type": alert_type,
            "message": message,
            "severity": self._get_alert_severity(alert_type)
        }
        
        self.alerts.append(alert)
        print(f"[ALERT] {alert['severity'].upper()}: {message}")
        
        # Save alerts
        self._save_alerts()
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Determine alert severity."""
        high_severity = ["fitness_drop", "high_cpu", "high_memory"]
        return "high" if alert_type in high_severity else "medium"
    
    def _save_alerts(self):
        """Save alerts to file."""
        Path("metrics").mkdir(exist_ok=True)
        
        with open("metrics/alerts.json", "w") as f:
            json.dump(self.alerts, f, indent=2)
    
    def display_dashboard(self, metrics: SystemMetrics):
        """Display real-time dashboard."""
        # Clear screen (ANSI escape code)
        print("\033[2J\033[H")
        
        print("="*60)
        print("         AutoEvolve Real-Time Monitoring Dashboard")
        print("="*60)
        print()
        
        print(f"Generation:        {metrics.generation}")
        print(f"Fitness Score:     {metrics.fitness_score:.4f}")
        print(f"Evolution Rate:    {metrics.evolution_rate:.4f}")
        print(f"Improvement Rate:  {metrics.improvement_rate:.6f}")
        print()
        
        print(f"Active Agents:     {metrics.active_agents}")
        print(f"CPU Usage:         {metrics.cpu_usage:.1f}%")
        print(f"Memory Usage:      {metrics.memory_usage:.1f}%")
        print()
        
        # Display recent alerts
        if self.alerts:
            print("Recent Alerts:")
            for alert in self.alerts[-3:]:
                print(f"  [{alert['severity'].upper()}] {alert['message']}")
            print()
        
        # Display fitness trend
        if len(self.metrics_history) >= 10:
            print("Fitness Trend (last 10):")
            recent_fitness = [m.fitness_score for m in self.metrics_history[-10:]]
            self._display_sparkline(recent_fitness)
            print()
        
        print("="*60)
        print(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to exit")
    
    def _display_sparkline(self, values: List[float]):
        """Display simple sparkline chart."""
        if not values:
            return
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val > min_val else 1.0
        
        chars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        line = ""
        for val in values:
            normalized = (val - min_val) / range_val
            idx = int(normalized * (len(chars) - 1))
            line += chars[idx]
        
        print(f"  {line}")
    
    def run_monitor(self, duration: Optional[float] = None):
        """Run monitoring loop."""
        print("[RealtimeMonitor] Starting monitoring loop...")
        
        start_time = time.time()
        
        try:
            while True:
                metrics = self.collect_metrics()
                self.display_dashboard(metrics)
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(self.refresh_interval)
        
        except KeyboardInterrupt:
            print("\n[RealtimeMonitor] Monitoring stopped by user")
        
        finally:
            self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics history."""
        Path("metrics").mkdir(exist_ok=True)
        
        metrics_data = [asdict(m) for m in self.metrics_history]
        
        with open("metrics/realtime_metrics.json", "w") as f:
            json.dump(metrics_data, f, indent=2)
        
        print(f"[RealtimeMonitor] Saved {len(self.metrics_history)} metric snapshots")


if __name__ == "__main__":
    monitor = RealtimeMonitor(refresh_interval=2.0)
    monitor.run_monitor()
