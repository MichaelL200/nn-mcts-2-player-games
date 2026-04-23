import torch
import torch.nn.functional as F
from .. import GameState


class ModelWrapper:
    def __init__(self, model: torch.nn.Module, encoder, device: str = 'cpu'):
        self.device = torch.device(device)
        self.model = model.to(self.device)
        self.model.eval()  # Ustawiamy model w tryb inferencji (nie trenujemy go w MCTS)
        self.encoder = encoder

    @staticmethod
    def load(path, device):
        from core.models import GameNet
        net = GameNet(action_size=1024).to(device)
        net.load_state_dict(torch.load(path, map_location=device, weights_only=True))
        return ModelWrapper(net, device)

    def predict(self, game_state: GameState):
        state_tensor = self.encoder(game_state)
        state_tensor = state_tensor.to(self.device)

        with torch.no_grad():
            policy_logits, value_tensor = self.model(state_tensor)
        policy_probs = F.softmax(policy_logits[0], dim=0).cpu().numpy()

        value = value_tensor.item()
        return policy_probs, value

