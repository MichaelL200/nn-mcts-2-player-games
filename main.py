import os
from src.gui import PygameCheckers, Gamemode
from src.checkers import Checkers
from src.models import ModelWrapper

if __name__ == "__main__":
    WIDTH = 1920
    HEIGHT = 850#1080
    MODEL_PATH = os.path.join("src", "models", "checkers_alphazero_model.pt")
    starting_state = Checkers().get_starting_state()  # Default position
    gamemode = Gamemode.PLAYER_VS_AI
    model = ModelWrapper.load(MODEL_PATH, "cuda") if os.path.exists(MODEL_PATH) else None
    game = PygameCheckers(WIDTH, HEIGHT, starting_state, gamemode, model)
    game.play_game()
