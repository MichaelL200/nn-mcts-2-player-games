from abc import ABC, abstractmethod
from .game_state import GameState, Move


class GameUI(ABC):
    @abstractmethod
    def render(self, state: GameState) -> None:
        pass

    @abstractmethod
    def get_player_move(self, state: GameState, valid_moves: list[Move]) -> Move | None:
        pass

    @abstractmethod
    def animate_move(self, state: GameState, move: Move) -> None:
        pass

    @abstractmethod
    def show_game_over(self, state: GameState) -> bool:
        pass

    @abstractmethod
    def quit(self) -> None:
        pass
