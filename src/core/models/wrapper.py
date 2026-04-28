import os
import torch
import torch.nn.functional as F
from ..interfaces import GameState, StateEncoder


class ModelWrapper:
    def __init__(self, model: torch.nn.Module, encoder: StateEncoder, device: str = 'cpu'):
        self.device = torch.device(device)
        self.model = model.to(self.device)
        self.model.eval()  # Ustawiamy model w tryb inferencji (nie trenujemy go w MCTS)
        self.encoder = encoder

    @staticmethod
    def load(path: str, encoder: StateEncoder, device: str = "cpu") -> "ModelWrapper | None":
        if not os.path.exists(path):
            return None
        from . import GameNet
        print(f"Loading existing model from {path} on {device}...")
        net = GameNet(action_size=encoder.action_size, in_channels=encoder.input_channels).to(device)
        state_dict = torch.load(path, map_location=device, weights_only=True)
        net.load_state_dict(state_dict)
        return ModelWrapper(net, encoder, device)

    @staticmethod
    def load_or_new(path: str, encoder: StateEncoder, device: str = "cpu") -> "ModelWrapper":
        model = ModelWrapper.load(path, encoder, device)
        if model is not None:
            return model
        from .architecture import GameNet
        net = GameNet(action_size=encoder.action_size, in_channels=encoder.input_channels)
        return ModelWrapper(net, encoder, device)

    def save(self, path: str) -> None:
        project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        model_path = os.path.join(project_path, path)
        if hasattr(self.model, "module"):
            state_dict = self.model.module.state_dict()
        else:
            state_dict = self.model.state_dict()
        torch.save(state_dict, model_path)

    def predict(self, game_state: GameState):
        state_tensor = self.encoder.encode(game_state)
        state_tensor = state_tensor.to(self.device)

        with torch.no_grad():
            policy_logits, value_tensor = self.model(state_tensor)
        policy_probs = F.softmax(policy_logits[0], dim=0).cpu().numpy()

        value = value_tensor.item()
        return policy_probs, value
