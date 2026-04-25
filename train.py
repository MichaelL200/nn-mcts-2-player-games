import os
import torch
from src.core.models.architecture import GameNet
from src.core.models.wrapper import ModelWrapper
from src.core.training.trainer import Trainer, TrainerConfig
from src.games.checkers.checkers import Checkers
from src.games.checkers.encoder import CheckersEncoder


CONFIG = TrainerConfig(
    episodes=50,
    mcts_time=0.5,
    batch_size=64,
    iterations=10,
    epochs=5,
    num_batches=100,
    max_moves=200,
    explore_rate=1.41,
    learning_rate=0.001,
    weight_decay=1e-4,
    buffer_size=10000,
)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = os.path.join("src", "models", "checkers_alphazero_model.pt")


game = Checkers()
encoder = CheckersEncoder()

net = GameNet(
    action_size=game.action_size,
    in_channels=encoder.input_channels,
).to(DEVICE)

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_PATH)
if os.path.exists(model_path):
    print(f"Found existing model at {model_path}. Resuming incremental training...")
    net.load_state_dict(torch.load(model_path, map_location=DEVICE, weights_only=True))
else:
    print("No existing model found. Starting training from scratch.")

model = ModelWrapper(net, encoder, device=DEVICE)

if __name__ == "__main__":
    trainer = Trainer(
        game=game,
        model=model,
        model_path=MODEL_PATH,
        config=CONFIG,
        device=DEVICE,
    )
    trainer.train()
