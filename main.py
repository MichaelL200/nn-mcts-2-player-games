import argparse
import os
import torch
from src.games import GAMES
from src.core import ModelWrapper, Gamemode, GameLoop, MCTSTree


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", choices=GAMES.keys(), default="checkers")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    entry = GAMES[args.game]

    WIDTH = 1920
    HEIGHT = 850  # 1080
    MODEL_PATH = os.path.join("src", "core", "models", entry["model_file"])

    game = entry["simulation"]()
    ui = entry["ui"](WIDTH, HEIGHT)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ModelWrapper.load(MODEL_PATH, game.encoder, device)
    if model is None:
        print(f"WARNING: No trained model found at {MODEL_PATH}")
        print("         The AI will use classic MCTS with random rollouts.")
        print(f"         To train the neural network, run: python train.py --game {args.game}")

    ai = MCTSTree(game, model, 1.41, 1)
    loop = GameLoop(game, ui, gamemode=Gamemode.PLAYER_VS_AI, ai=ai)
    loop.run(game.get_starting_state())
