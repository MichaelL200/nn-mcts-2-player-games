import os
import torch
from src.games import Checkers, CheckersUI
from src.core import ModelWrapper, Gamemode, GameLoop, MCTSTree

if __name__ == "__main__":

    WIDTH = 1920
    HEIGHT = 850  # 1080
    MODEL_PATH = os.path.join("src", "core", "models", "checkers_alphazero_model.pt")

    game = Checkers()
    ui = CheckersUI(WIDTH, HEIGHT)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ModelWrapper.load(MODEL_PATH, game.encoder, device)
    if model is None:
        print(f"WARNING: No trained model found at {MODEL_PATH}")
        print("         The AI will use classic MCTS with random rollouts.")
        print("         To train the neural network, run train.py")
    
    ai =  MCTSTree(game, model, 1.41, 1)
    loop = GameLoop(game, ui, gamemode=Gamemode.AI_VS_AI, ai=ai)
    loop.run(game.get_starting_state())
