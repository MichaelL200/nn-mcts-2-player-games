import os
import torch
from src.games import Checkers, CheckersUI
from src.core import ModelWrapper, Gamemode, GameLoop, MCTSTree

if __name__ == "__main__":

    WIDTH = 1920
    HEIGHT = 850  # 1080
    MODEL_PATH = os.path.join("src", "models", "checkers_alphazero_model.pt")

    game = Checkers()
    ui = CheckersUI(WIDTH, HEIGHT)

    if os.path.exists(MODEL_PATH):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading existing model from {MODEL_PATH} on {device}...")
        model = ModelWrapper.load(MODEL_PATH, device)
    else:
        print(f"WARNING: No trained model found at {MODEL_PATH}")
        print("         The AI will use classic MCTS with random rollouts.")
        print("         To train the neural network, run train.py")
        model = None
    ai =  MCTSTree(game, model, 1.41, 1)
    loop = GameLoop(game, ui, gamemode=Gamemode.PLAYER_VS_AI, ai=ai)
    loop.run(game.get_starting_state())
