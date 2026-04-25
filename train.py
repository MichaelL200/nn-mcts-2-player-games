import os
import torch
from src.core.models.wrapper import ModelWrapper
from src.core.training.trainer import Trainer, TrainerConfig
from src.games.checkers.checkers import Checkers


CONFIG = TrainerConfig(
    episodes=5,
    mcts_time=0.5,
    batch_size=64,
    iterations=1,
    epochs=1,
    num_batches=100,
    max_moves=50,
    explore_rate=1.41,
    learning_rate=0.001,
    weight_decay=1e-4,
    buffer_size=10000,
)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = os.path.join("src", "core", "models", "checkers_alphazero_model.pt")


game = Checkers()

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_PATH)
model = ModelWrapper.load_or_new(model_path, game.encoder, device=DEVICE)

if __name__ == "__main__":
    trainer = Trainer(
        game=game,
        model=model,
        model_path=model_path,
        config=CONFIG,
        device=DEVICE,
    )
    trainer.train()
