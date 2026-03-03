"""Distributed evolution system using multi-agent parallelization."""

import asyncio
import multiprocessing as mp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed


@dataclass
class EvolutionTask:
    """Represents a parallel evolution task."""
    task_id: int
    code_variant: str
    strategy: str
    fitness_target: float


class DistributedEvolver:
    """Distributed evolution using parallel processing and agent collaboration."""
    
    def __init__(self, num_agents: int = None):
        self.num_agents = num_agents or mp.cpu_count()
        self.agent_pool = None
        self.task_queue = []
        self.results = []
        self.generation = 0
        
        print(f"[DistributedEvolver] Initialized with {self.num_agents} parallel agents")
    
    def distribute_evolution(self, population: List[Dict], fitness_func: callable) -> List[Dict]:
        """Distribute evolution across multiple parallel agents."""
        print(f"[DistributedEvolver] Distributing {len(population)} individuals across {self.num_agents} agents")
        
        # Create tasks
        tasks = []
        for i, individual in enumerate(population):
            task = EvolutionTask(
                task_id=i,
                code_variant=str(individual),
                strategy=individual.get('strategy', 'default'),
                fitness_target=individual.get('target_fitness', 0.8)
            )
            tasks.append(task)
        
        # Execute in parallel
        evaluated = []
        with ProcessPoolExecutor(max_workers=self.num_agents) as executor:
            futures = {executor.submit(self._evaluate_individual, task, fitness_func): task for task in tasks}
            
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    evaluated.append(result)
                    print(f"[DistributedEvolver] Agent completed task {task.task_id}: fitness={result.get('fitness', 0):.4f}")
                except Exception as e:
                    print(f"[DistributedEvolver] Task {task.task_id} failed: {e}")
        
        print(f"[DistributedEvolver] Completed {len(evaluated)}/{len(tasks)} evaluations")
        return evaluated
    
    @staticmethod
    def _evaluate_individual(task: EvolutionTask, fitness_func: callable) -> Dict:
        """Evaluate individual in separate process."""
        try:
            fitness = fitness_func(task.code_variant)
            return {
                'task_id': task.task_id,
                'variant': task.code_variant,
                'strategy': task.strategy,
                'fitness': fitness,
                'success': fitness >= task.fitness_target
            }
        except Exception as e:
            return {
                'task_id': task.task_id,
                'variant': task.code_variant,
                'strategy': task.strategy,
                'fitness': 0.0,
                'success': False,
                'error': str(e)
            }
    
    async def async_evolve(self, population: List[Dict]) -> List[Dict]:
        """Asynchronous evolution for maximum throughput."""
        print("[DistributedEvolver] Starting async evolution...")
        
        async def evolve_async(individual: Dict) -> Dict:
            # Simulate async evolution
            await asyncio.sleep(0.1)  # Simulate computation
            fitness = np.random.rand()
            individual['fitness'] = fitness
            return individual
        
        tasks = [evolve_async(ind) for ind in population]
        results = await asyncio.gather(*tasks)
        
        print(f"[DistributedEvolver] Async evolution complete: {len(results)} results")
        return results
    
    def island_model_evolution(self, num_islands: int = 4, migration_rate: float = 0.1) -> Dict:
        """Island model for parallel evolution with periodic migration."""
        print(f"[DistributedEvolver] Island model with {num_islands} islands")
        
        # Initialize islands with sub-populations
        island_size = 20
        islands = [
            {'id': i, 'population': [{'fitness': 0.0} for _ in range(island_size)]}
            for i in range(num_islands)
        ]
        
        num_generations = 10
        
        for gen in range(num_generations):
            print(f"[DistributedEvolver] Island Generation {gen}")
            
            # Evolve each island independently
            with ProcessPoolExecutor(max_workers=num_islands) as executor:
                futures = {executor.submit(self._evolve_island, island): island for island in islands}
                
                for future in as_completed(futures):
                    island = futures[future]
                    try:
                        evolved_island = future.result()
                        island['population'] = evolved_island['population']
                    except Exception as e:
                        print(f"[DistributedEvolver] Island {island['id']} evolution failed: {e}")
            
            # Migration phase
            if gen % 3 == 0 and gen > 0:
                self._migrate_individuals(islands, migration_rate)
        
        # Collect best individuals from all islands
        all_individuals = []
        for island in islands:
            all_individuals.extend(island['population'])
        
        all_individuals.sort(key=lambda x: x.get('fitness', 0), reverse=True)
        
        return {
            'best_individual': all_individuals[0],
            'islands': islands,
            'total_individuals': len(all_individuals)
        }
    
    @staticmethod
    def _evolve_island(island: Dict) -> Dict:
        """Evolve population on a single island."""
        population = island['population']
        
        # Simulate evolution
        for individual in population:
            # Mutation
            mutation = np.random.randn() * 0.1
            individual['fitness'] = max(0, min(1, individual.get('fitness', 0.5) + mutation))
        
        # Selection
        population.sort(key=lambda x: x['fitness'], reverse=True)
        
        return island
    
    def _migrate_individuals(self, islands: List[Dict], migration_rate: float):
        """Migrate best individuals between islands."""
        num_migrants = max(1, int(len(islands[0]['population']) * migration_rate))
        
        print(f"[DistributedEvolver] Migrating {num_migrants} individuals per island")
        
        for i in range(len(islands)):
            source = islands[i]
            target = islands[(i + 1) % len(islands)]  # Ring topology
            
            # Get best individuals from source
            source['population'].sort(key=lambda x: x.get('fitness', 0), reverse=True)
            migrants = source['population'][:num_migrants]
            
            # Send to target, replace worst individuals
            target['population'].sort(key=lambda x: x.get('fitness', 0), reverse=True)
            target['population'] = target['population'][:-num_migrants] + migrants
    
    def hierarchical_evolution(self, levels: int = 3) -> Dict:
        """Hierarchical evolution with coarse-to-fine optimization."""
        print(f"[DistributedEvolver] Hierarchical evolution with {levels} levels")
        
        results = {'levels': []}
        population_size = 50
        
        for level in range(levels):
            print(f"[DistributedEvolver] Level {level + 1}/{levels}")
            
            # Increase resolution at each level
            granularity = 2 ** level
            
            # Evolve at current level
            population = [{'fitness': np.random.rand(), 'level': level} for _ in range(population_size)]
            population.sort(key=lambda x: x['fitness'], reverse=True)
            
            level_result = {
                'level': level,
                'granularity': granularity,
                'best_fitness': population[0]['fitness'],
                'population_size': len(population)
            }
            results['levels'].append(level_result)
            
            # Refine best solutions for next level
            population = population[:population_size // 2]  # Keep top 50%
        
        return results
