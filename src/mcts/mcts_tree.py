import time
import numpy as np
from copy import deepcopy
from multiprocessing import Process, Manager

from .mcts_node import MCTSNode
from ..interfaces import GameState, Move, GameSimulation


class MCTSTree:
    """
    Monte Carlo Tree Search is a method for finding optimal decision in a given game state.
    This class provides methods for running algorithm in given game environment.
    """

    def __init__(self, game: GameSimulation, model, explore_rate: float, time_limit: float) -> None:
        self.root = None
        self.game = game
        self.explore_rate = explore_rate
        self.time_limit = time_limit    # time in seconds
        self.model = model

    def mcts_search(self, init_state: GameState) -> Move:
        """
        Implementation of basic algorithm that involves building a search tree
        until predefined computational budget - time.
        :param init_state: current game state
        :return: action that leads to the best child of init_state
        """
        self.root = MCTSNode(deepcopy(init_state),
                                 self.game.get_moves(init_state))
        self._expansion(self.root)
        start_time = time.time()
        while (time.time() - start_time) < self.time_limit:
            node = self._selection(self.root)
            if not self.game.is_terminal(node.game_state):
                reward = self._expansion(node)
            else:
                reward = self.game.reward(node.game_state, node.game_state.active_player)
            self._backprop(node, reward)
            
        return self._get_best_child().prev_move

    def _selection(self, current_node: MCTSNode) -> MCTSNode:
        while not self.game.is_terminal(current_node.game_state):
            if len(current_node.moves_not_taken) != 0:
                return current_node
            current_node = max(current_node.children_nodes, key=lambda node: node.get_ucb_score())
            
        return current_node
    
    def _expansion(self, leaf_node: MCTSNode) -> MCTSNode:
        policy, value = self.model.predict(leaf_node.game_state)
        for move in leaf_node.moves_not_taken:
            p_move = policy[self.game.move_to_index(move)]
            new_state = self.game.make_move(deepcopy(leaf_node.game_state), move)
            
            new_node = MCTSNode(
                new_state, 
                self.game.get_moves(new_state), 
                move, 
                leaf_node,
                p_value=p_move
            )
            leaf_node.children_nodes.append(new_node)
        
        leaf_node.moves_not_taken = []
        return value 

    def _backprop(self, leaf_node: MCTSNode, reward: float) -> None:
        while True:
            leaf_node.q_value+=reward
            reward = -reward
            leaf_node.visit_count += 1
            if leaf_node.parent_node is None:
                return
            leaf_node = leaf_node.parent_node

    def _get_best_child(self) -> MCTSNode:
        root_children = [child for child in self.root.children_nodes]
        return max(root_children, key=lambda x: x.visit_count)

    def get_move_probs(self) -> str:
        sorted_kids = sorted(self.root.children_nodes,
                             key=lambda x: int(x.prev_move))
        lst = [
            f"{child.prev_move} {child.q_value/child.visit_count:.3}" for child in sorted_kids]
        return " ".join(lst) + '\n'

    def get_action_prob(self) -> np.ndarray:
        # function for training
        action_probs = np.zeros(self.model.model.action_size, dtype=np.float32)
        
        counts = [child.visit_count for child in self.root.children_nodes]
        total_visits = sum(counts)
        
        if total_visits == 0:
            return action_probs # Zabezpieczenie przed błędem dzielenia przez 0
            
        for child in self.root.children_nodes:
            action_idx = self.game.move_to_index(child.prev_move)
            action_probs[action_idx] = child.visit_count / total_visits
            
        return action_probs