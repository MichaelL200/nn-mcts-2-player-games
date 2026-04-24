from enum import Enum
from .interfaces.game_simulation import GameSimulation
from .interfaces.game_ui import GameUI
from .interfaces.game_state import GameState
from .mcts import MCTSTree


class Gamemode(Enum):
    PLAYER_VS_PLAYER = 1
    PLAYER_VS_AI = 2
    AI_VS_AI = 3

class GameLoop:
    def __init__(self, game: GameSimulation, ui: GameUI, gamemode: Gamemode, ai: MCTSTree) -> None:
        self.game = game
        self.ui = ui
        self.gamemode = gamemode
        self.ai = ai

    def run(self, state: GameState) -> None:
        while True:
            state = self._play(state)
            restart = self.ui.show_game_over(state)
            if restart:
                state = self.game.get_starting_state()
            else:
                break
        self.ui.quit()

    def _play(self, state: GameState) -> GameState:
        human_player = state.active_player

        while self.game.is_terminal(state) is False:
            self.ui.render(state)

            if self.gamemode == Gamemode.PLAYER_VS_PLAYER:
                state = self._handle_player_turn(state)

            elif self.gamemode == Gamemode.AI_VS_AI:
                state = self._handle_ai_turn(state)

            elif self.gamemode == Gamemode.PLAYER_VS_AI:
                if state.active_player == human_player:
                    state = self._handle_player_turn(state)
                else:
                    state = self._handle_ai_turn(state)

        self.ui.render(state)
        return state
    
    def _handle_player_turn(self, state: GameState) -> GameState:
        valid_moves = self.game.get_moves(state)
        move = self.ui.get_player_move(state, valid_moves)
        if move is not None:
            self.ui.animate_move(state, move)
            return self.game.make_move(state, move)
        return state
    
    def _handle_ai_turn(self, state: GameState) -> GameState:
        move = self.ai.mcts_search(state)
        self.ui.animate_move(state, move)
        return self.game.make_move(state, move)