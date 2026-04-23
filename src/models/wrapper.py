import torch
import torch.nn.functional as F
from ..core import GameState
from ..checkers import CheckersPiece
from ..checkers import CheckersPlayer


class ModelWrapper:
    def __init__(self, model: torch.nn.Module, device: str = 'cpu'):
        self.device = torch.device(device)
        self.model = model.to(self.device)
        self.model.eval()  # Ustawiamy model w tryb inferencji (nie trenujemy go w MCTS)

    @staticmethod
    def load(path, device):
        from src.models import CheckersNet
        net = CheckersNet(action_size=1024).to(device)
        net.load_state_dict(torch.load(path, map_location=device, weights_only=True))
        return ModelWrapper(net, device)

        return ModelWrapper(net, device)

    def predict(self, game_state: GameState):
        state_tensor = self.state_to_tensor(game_state)
        state_tensor = state_tensor.to(self.device)

        with torch.no_grad():
            policy_logits, value_tensor = self.model(state_tensor)
        policy_probs = F.softmax(policy_logits[0], dim=0).cpu().numpy()

        value = value_tensor.item()
        return policy_probs, value

    def state_to_tensor(self, game_state: GameState) -> torch.Tensor:
        tensor = torch.zeros(1, 5, 8, 8, dtype=torch.float32)
        board = game_state.board
        for index in range(32):
            piece = board.get_piece(index)

            if piece is None or piece == CheckersPiece.EMPTY:
                continue
            row = index // 4
            if row % 2 == 0:
                col = (index % 4) * 2
            else:
                col = (index % 4) * 2 + 1

            if piece == CheckersPiece.WHITE:
                tensor[0, 0, row, col] = 1.0
            elif piece == CheckersPiece.WHITE_QUEEN:
                tensor[0, 1, row, col] = 1.0
            elif piece == CheckersPiece.BLACK:
                tensor[0, 2, row, col] = 1.0
            elif piece == CheckersPiece.BLACK_QUEEN:
                tensor[0, 3, row, col] = 1.0

        if game_state.active_player == CheckersPlayer.WHITE:
            tensor[0, 4, :, :] = 1.0
        else:
            tensor[0, 4, :, :] = 0.0

        return tensor
