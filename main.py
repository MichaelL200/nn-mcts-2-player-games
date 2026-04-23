import os
import torch
from src.gui import PygameCheckers, Gamemode
from src.games import Checkers
from src.models import ModelWrapper

if __name__ == "__main__":

    WIDTH = 1920
    HEIGHT = 850  # 1080
    MODEL_PATH = os.path.join("src", "models", "checkers_alphazero_model.pt")

    starting_state = Checkers().get_starting_state()  # Default position
    gamemode = Gamemode.PLAYER_VS_AI

    if os.path.exists(MODEL_PATH):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading existing model from {MODEL_PATH} on {device}...")
        model = ModelWrapper.load(MODEL_PATH, device)
    else:
        print(f"WARNING: No trained model found at {MODEL_PATH}")
        print("         The AI will use classic MCTS with random rollouts.")
        print("         To train the neural network, run train.py")
        model = None

    game = PygameCheckers(WIDTH, HEIGHT, starting_state, gamemode, model)
    game.play_game()
