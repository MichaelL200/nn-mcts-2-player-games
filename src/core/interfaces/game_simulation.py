from abc import ABC, abstractmethod
from .game_state import GameState, Move, Player


class GameSimulation(ABC):
    @abstractmethod
    def is_terminal(self, game_state: GameState) -> bool:
        pass

    @abstractmethod
    def get_moves(self, game_state: GameState) -> list[Move]:
        pass

    @abstractmethod
    def make_move(self, game_state: GameState, move: Move) -> GameState:
        pass

    @abstractmethod
    def make_random_move(self, game_state: GameState) -> GameState:
        pass

    @abstractmethod
    def get_starting_state(self) -> GameState:
        pass

    @abstractmethod
    def reward(self, game_state: GameState, desired_winner: Player) -> int | None:
        # reward should return 1,0,-1 base on player value.
        # if player 1 won then reward is 1, if he lost then reward is -1
        # but if player -1 won then reward is -1, etc...
        # None is returned when game is not finished yet
        pass
