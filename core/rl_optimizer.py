"""Reinforcement learning optimizer for learning optimal evolution strategies."""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path
from collections import deque


@dataclass
class RLState:
    """State representation for RL agent."""
    code_features: np.ndarray
    current_fitness: float
    generation: int
    previous_actions: List[int]


@dataclass
class RLAction:
    """Action representation for RL agent."""
    action_id: int
    strategy: str
    parameters: Dict[str, float]


class QLearningOptimizer:
    """Q-Learning agent for optimizing evolution strategies."""
    
    def __init__(self, num_states: int = 100, num_actions: int = 10):
        self.num_states = num_states
        self.num_actions = num_actions
        
        # Q-table
        self.q_table = np.zeros((num_states, num_actions))
        
        # Hyperparameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # Exploration rate
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.01
        
        # Experience replay
        self.replay_buffer = deque(maxlen=10000)
        
        # Actions mapping
        self.actions = self._define_actions()
        
        # Training history
        self.training_history = []
        self.episode = 0
        
        print(f"[RLOptimizer] Initialized Q-Learning with {num_states} states, {num_actions} actions")
    
    def _define_actions(self) -> List[RLAction]:
        """Define available actions for the RL agent."""
        actions = [
            RLAction(0, "increase_mutation", {"rate": 0.05}),
            RLAction(1, "decrease_mutation", {"rate": -0.05}),
            RLAction(2, "increase_population", {"size": 5}),
            RLAction(3, "decrease_population", {"size": -5}),
            RLAction(4, "focus_performance", {"weight": 0.1}),
            RLAction(5, "focus_quality", {"weight": 0.1}),
            RLAction(6, "balance_objectives", {"weight": 0.0}),
            RLAction(7, "aggressive_selection", {"pressure": 0.1}),
            RLAction(8, "exploration_mode", {"exploration": 0.2}),
            RLAction(9, "exploitation_mode", {"exploration": -0.2})
        ]
        return actions
    
    def get_state_index(self, state: RLState) -> int:
        """Convert continuous state to discrete state index."""
        # Hash state features to index
        fitness_bin = int(state.current_fitness * 10)
        gen_bin = min(state.generation // 10, 9)
        state_idx = fitness_bin * 10 + gen_bin
        return min(state_idx, self.num_states - 1)
    
    def select_action(self, state: RLState, training: bool = True) -> RLAction:
        """Select action using epsilon-greedy policy."""
        state_idx = self.get_state_index(state)
        
        if training and np.random.rand() < self.epsilon:
            # Explore: random action
            action_idx = np.random.randint(self.num_actions)
        else:
            # Exploit: best known action
            action_idx = np.argmax(self.q_table[state_idx])
        
        return self.actions[action_idx]
    
    def update_q_value(self, state: RLState, action: RLAction, reward: float, next_state: RLState):
        """Update Q-value using Q-learning update rule."""
        state_idx = self.get_state_index(state)
        next_state_idx = self.get_state_index(next_state)
        action_idx = action.action_id
        
        # Q-learning update
        current_q = self.q_table[state_idx, action_idx]
        max_next_q = np.max(self.q_table[next_state_idx])
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_idx, action_idx] = new_q
        
        # Store in replay buffer
        self.replay_buffer.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state
        })
    
    def train_episode(self, initial_state: RLState, evolution_function: callable, max_steps: int = 50) -> float:
        """Train for one episode."""
        state = initial_state
        total_reward = 0.0
        
        for step in range(max_steps):
            # Select action
            action = self.select_action(state, training=True)
            
            # Execute action and get reward
            next_state, reward, done = evolution_function(state, action)
            
            # Update Q-value
            self.update_q_value(state, action, reward, next_state)
            
            total_reward += reward
            state = next_state
            
            if done:
                break
        
        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        # Record episode
        self.episode += 1
        self.training_history.append({
            'episode': self.episode,
            'total_reward': total_reward,
            'epsilon': self.epsilon,
            'steps': step + 1
        })
        
        if self.episode % 10 == 0:
            print(f"[RLOptimizer] Episode {self.episode}: Reward={total_reward:.2f}, Epsilon={self.epsilon:.3f}")
        
        return total_reward
    
    def experience_replay(self, batch_size: int = 32):
        """Train on random batch from experience replay buffer."""
        if len(self.replay_buffer) < batch_size:
            return
        
        # Sample random batch
        indices = np.random.choice(len(self.replay_buffer), batch_size, replace=False)
        batch = [self.replay_buffer[i] for i in indices]
        
        # Update Q-values for batch
        for experience in batch:
            self.update_q_value(
                experience['state'],
                experience['action'],
                experience['reward'],
                experience['next_state']
            )
    
    def save_model(self, path: str = "metrics/rl_model.json"):
        """Save Q-table and training history."""
        Path("metrics").mkdir(exist_ok=True)
        
        model_data = {
            'q_table': self.q_table.tolist(),
            'training_history': self.training_history,
            'episode': self.episode,
            'epsilon': self.epsilon
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        print(f"[RLOptimizer] Model saved to {path}")
    
    def load_model(self, path: str = "metrics/rl_model.json"):
        """Load Q-table and training history."""
        if not Path(path).exists():
            print(f"[RLOptimizer] No saved model found at {path}")
            return
        
        with open(path, 'r') as f:
            model_data = json.load(f)
        
        self.q_table = np.array(model_data['q_table'])
        self.training_history = model_data['training_history']
        self.episode = model_data['episode']
        self.epsilon = model_data['epsilon']
        
        print(f"[RLOptimizer] Model loaded from {path}")


class PolicyGradientOptimizer:
    """Policy gradient optimizer for continuous action spaces."""
    
    def __init__(self, state_dim: int = 10, action_dim: int = 5):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Simple linear policy (in production would use neural network)
        self.policy_weights = np.random.randn(state_dim, action_dim) * 0.01
        self.value_weights = np.random.randn(state_dim) * 0.01
        
        self.learning_rate = 0.01
        self.trajectory_buffer = []
        
        print(f"[PolicyGradient] Initialized with state_dim={state_dim}, action_dim={action_dim}")
    
    def policy(self, state: np.ndarray) -> np.ndarray:
        """Compute policy (action probabilities)."""
        logits = np.dot(state, self.policy_weights)
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        return probs
    
    def value(self, state: np.ndarray) -> float:
        """Compute state value."""
        return np.dot(state, self.value_weights)
    
    def sample_action(self, state: np.ndarray) -> int:
        """Sample action from policy."""
        probs = self.policy(state)
        action = np.random.choice(self.action_dim, p=probs)
        return action
    
    def update_policy(self, states: List[np.ndarray], actions: List[int], rewards: List[float]):
        """Update policy using policy gradient."""
        # Compute returns
        returns = self._compute_returns(rewards)
        
        # Normalize returns
        returns = (returns - np.mean(returns)) / (np.std(returns) + 1e-8)
        
        # Update policy
        for state, action, ret in zip(states, actions, returns):
            # Compute advantage
            advantage = ret - self.value(state)
            
            # Policy gradient
            probs = self.policy(state)
            grad = np.outer(state, self._one_hot(action, self.action_dim) - probs)
            self.policy_weights += self.learning_rate * advantage * grad
            
            # Value function update
            value_error = ret - self.value(state)
            self.value_weights += self.learning_rate * value_error * state
    
    def _compute_returns(self, rewards: List[float], gamma: float = 0.99) -> np.ndarray:
        """Compute discounted returns."""
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        return np.array(returns)
    
    def _one_hot(self, idx: int, size: int) -> np.ndarray:
        """Create one-hot vector."""
        vec = np.zeros(size)
        vec[idx] = 1
        return vec
