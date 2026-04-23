from __future__ import annotations
import math
from ..interfaces import GameState, Move


class MCTSNode:
    def __init__(self,
                 game_state: GameState,
                 possible_state_moves: list[Move],
                 prev_move: Move | None = None,
                 parent_node: MCTSNode | None = None,
                 p_value: float = 0.0
                 ) -> None:

        self.game_state = game_state
        self.parent_node = parent_node
        # move that was taken in order to get from parent node to this node. None when root node
        self.prev_move = prev_move
        self.moves_not_taken = possible_state_moves
        self.P = p_value

        self.children_nodes: list[MCTSNode] = []
        self.visit_count: int = 0
        self.q_value: float = 0

    def get_ucb_score(self, c_puct: float = 1.0) -> float:
        if self.visit_count == 0:
            return c_puct * self.P * math.sqrt(self.parent_node.visit_count + 1)
        q_mean = self.q_value / self.visit_count
        u_score = c_puct * self.P * (math.sqrt(self.parent_node.visit_count) / (1 + self.visit_count))
        return q_mean + u_score
