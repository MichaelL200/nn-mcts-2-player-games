import argparse
import os
import torch
from src.core.models.wrapper import ModelWrapper
from src.core.training.trainer import Trainer, TrainerConfig
from src.games import GAMES


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", choices=GAMES.keys(), default="checkers")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    entry = GAMES[args.game]

    game = entry["simulation"]()

    model_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "src", "core", "models", entry["model_file"],
    )
    model = ModelWrapper.load_or_new(model_path, game.encoder, device=DEVICE)

    trainer = Trainer(
        game=game,
        model=model,
        model_path=model_path,
        config=CONFIG,
        device=DEVICE,
    )
    trainer.train()
