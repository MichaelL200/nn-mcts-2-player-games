from abc import ABC, abstractmethod
import torch
from .game_state import GameState, Move

class StateEncoder(ABC):
    @property
    @abstractmethod
    def input_channels(self) -> int:
        pass

    @property
    @abstractmethod
    def action_size(self) -> int:
        pass

    @abstractmethod
    def move_to_index(self, move: Move) -> int:
        pass

    @abstractmethod
    def encode(self, game_state: GameState) -> torch.Tensor:
        pass
