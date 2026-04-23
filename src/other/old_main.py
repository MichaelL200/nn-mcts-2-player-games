import random
from os import system
from time import sleep
from core.mcts import MCTSTree as MCTS
from src.games import (
    Checkers,
    CheckersPlayer,
    # CheckersBoard,
    # CheckersPiece,
    # CheckersState,
)
# from copy import deepcopy
# from collections import Counter
# from tqdm import tqdm
# import numpy as np

game = Checkers()
mcts1 = MCTS(game, 1.41, 200)
mcts2 = MCTS(game, 1.41, 1600)


def run_sim():
    state = game.get_starting_state()
    while True:
        move = mcts1.mcts_search(state)
        state = game.make_move(state, move)
        if game.is_terminal(state):
            return game.reward(state, CheckersPlayer.WHITE)

        move = mcts2.mcts_search(state)
        state = game.make_move(state, move)
        if game.is_terminal(state):
            return game.reward(state, CheckersPlayer.BLACK)


def checkers_demo():
    game = Checkers()
    state = game.get_starting_state()
    while True:
        moves = game.get_moves(state)
        move = random.choice(moves)
        state = game.make_move(state, move)

        system("clear")
        print(state.board)
        print(moves)
        print(move)

        if game.is_terminal(state):
            print(game.reward(state))
            break


def play_versus_mcts():
    state = game.get_starting_state()

    while game.is_terminal(state) is False:
        system("clear")
        print(state.board)
        sleep(1)

        move = mcts1.mcts_search(state)
        state = game.make_move(state, move)

        system("clear")
        print(state.board)
        print(f"MCTS move: {move}")
        sleep(1)

        player_move = input("Your Move: ")
        state = game.make_move(state, player_move)


def mcts_vs_random():
    state = game.get_starting_state()

    while game.is_terminal(state) is False:
        move = mcts1.mcts_search(state)
        state = game.make_move(state, move)
        system("clear")
        print(state.board)
        print(f"MCTS move: {move}")
        sleep(2)
        if game.is_terminal(state):
            break

        move = random.choice(game.get_moves(state))
        state = game.make_move(state, move)
        system("clear")
        print(state.board)
        print(f"Random move: {move}")
        sleep(2)


def main():
    pass
    # outcomes = []
    # for _ in tqdm(range(100)):
    #   outcomes.append(run_sim())
    # print(Counter(outcomes))

    # play_versus_mcts()
    # mcts_vs_random()


if __name__ == "__main__":
    main()
