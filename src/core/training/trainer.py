import torch
import torch.optim as optim
import torch.nn.functional as F
from copy import deepcopy
from dataclasses import dataclass
import torch.distributed as dist
from ..interfaces import GameSimulation
from ..mcts.mcts_tree import MCTSTree
from ..models.wrapper import ModelWrapper
from .replay_buffer import ReplayBuffer
import numpy as np


@dataclass
class TrainerConfig:
    episodes: int = 50
    mcts_time: float = 0.5
    batch_size: int = 64
    iterations: int = 10
    epochs: int = 5
    num_batches: int = 100
    max_moves: int = 200
    explore_rate: float = 1.41
    learning_rate: float = 0.0001
    weight_decay: float = 1e-4
    buffer_size: int = 10000
    temperature: float = 0.7


class Trainer:
    def __init__(
            self, game: GameSimulation, model: ModelWrapper, model_path: str,
            config: TrainerConfig, device: str, rank: int, world_size: int
    ) -> None:
        self.game = game
        self.model = model
        self.model_path = model_path
        self.config = config
        self.device = device
        self.rank = rank
        self.world_size = world_size
        self.buffer = ReplayBuffer(max_size=config.buffer_size)
        self.optimizer = optim.Adam(
            self.model.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
        )

    def train(self) -> None:
        for iteration in range(1, self.config.iterations + 1):
            if self.rank == 0:
                print(f"---------Iteration: {iteration}/{self.config.iterations}---------", flush=True)

            self._self_play_phase()
            if dist.is_initialized():
                dist.barrier()

            if len(self.buffer) > self.config.batch_size:
                self._training_phase()
                if self.rank == 0:
                    self._save_model()
            if dist.is_initialized():
                dist.barrier()

    def _self_play_phase(self) -> None:
        self.model.model.eval()
        for episode in range(self.config.episodes):
            if self.rank == 0:
                print(f"Processing game: {episode + 1}/{self.config.episodes}...", flush=True)
            history, winner = self._play_self_play_game()
            if self.rank == 0:
                print(f"Game finished. Winner: {winner}, num moves: {len(history)}", flush=True)
            self.buffer.save_game(history, winner)

    def _play_self_play_game(self) -> tuple:
        state = self.game.get_starting_state()
        mcts = MCTSTree(
            game=self.game, model=self.model, explore_rate=self.config.explore_rate,
            time_limit=self.config.mcts_time
        )

        game_history = []
        move_count = 0
        player_before_move = state.active_player
        while not self.game.is_terminal(state):
            search_temperature = self.config.temperature if move_count < 30 else None
            best_move = mcts.mcts_search(state, temperature=search_temperature, is_training=True)
            action_prob = mcts.get_action_prob()
            state_tensor = self.model.encoder.encode(state)

            game_history.append((state_tensor, action_prob, state.active_player))
            state = self.game.make_move(deepcopy(state), best_move)
            move_count += 1

            if move_count >= self.config.max_moves:
                if self.rank == 0:
                    print(f"{self.config.max_moves} moves reached, assuming draw.", flush=True)
                return game_history, 0
 
        #first_player = self.game.get_starting_state().active_player
        winner_value = self.game.reward(state, player_before_move)
        return game_history, winner_value

    def _training_phase(self) -> None:
        if self.rank == 0:
            print("Training neural network...", flush=True)
        self.model.model.train()
        all_phase_losses = []
        for epoch in range(self.config.epochs):
            epoch_losses = []
            for _ in range(self.config.num_batches):
                loss = self._training_step()
                epoch_losses.append(loss.item())
            if self.rank == 0:
                avg_epoch_loss = np.mean(epoch_losses)
                print(f"Epoch {epoch + 1}/{self.config.epochs} finished. Avg Loss: {avg_epoch_loss:.4f}", flush=True)
            all_phase_losses.extend(epoch_losses)
        if self.rank == 0 and all_phase_losses:
            global_avg = np.mean(all_phase_losses)
            print(f"Full Training Phase finished. Global Avg Loss: {global_avg:.4f}", flush=True)
 
        self.model.model.eval()

    def _training_step(self) -> torch.Tensor:
        states, target_policies, target_values = self.buffer.sample_batch(self.config.batch_size)
        states = states.to(self.device)
        target_policies = target_policies.to(self.device)
        target_values = target_values.to(self.device)

        self.optimizer.zero_grad()
        predicted_policy_logits, predicted_values = self.model.model(states)

        value_loss = F.mse_loss(predicted_values, target_values)
        pred_policy_log = F.log_softmax(predicted_policy_logits, dim=1)
        policy_loss = -(target_policies * pred_policy_log).sum(dim=1).mean()
        if self.rank ==0:
            print(f"Value loss: {value_loss.item():.4f}, Policy loss: {policy_loss.item():.4f}")
        total_loss = value_loss + policy_loss
        total_loss.backward()
        self.optimizer.step()
        return total_loss

    def _save_model(self) -> None:
        self.model.save(self.model_path)
