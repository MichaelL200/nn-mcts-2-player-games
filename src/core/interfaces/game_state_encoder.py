from abc import ABC, abstractmethod
import torch
from .game_state import GameState

class StateEncoder(ABC):
    @property
    @abstractmethod
    def input_channels(self) -> int:
        pass

    @abstractmethod
    def encode(self, game_state: GameState) -> torch.Tensor:
        pass