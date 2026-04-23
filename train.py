import os
import torch
import torch.optim as optim
import torch.nn.functional as F
from copy import deepcopy
from src.checkers import Checkers, CheckersPlayer
from src.models import CheckersNet, ModelWrapper
from src.core import MCTSTree, ReplayBuffer


EPISODES = 50
MCTS_TIME = 0.5
BATCH_SIZE = 64
ITERATIONS = 10
EPOCHS = 5
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = os.path.join("src", "models", "checkers_alphazero_model.pt")


def play_self_play_game(game, model):
    state = game.get_starting_state()
    mcts = MCTSTree(game=game, model=model, explore_rate=1.41, time_limit=MCTS_TIME)

    game_history = []
    move_count = 0

    while not game.is_terminal(state):
        best_move_str = mcts.mcts_search(state)
        action_prob = mcts.get_action_prob()
        state_tensor = model.state_to_tensor(state)

        game_history.append((state_tensor, action_prob, state.active_player))
        state = game.make_move(deepcopy(state), best_move_str)
        move_count += 1

        if move_count >= 200:
            print("200 Moves assuming this is draw situation.", flush=True)
            return game_history, 0

    winner_value = game.reward(state, CheckersPlayer.WHITE)

    return game_history, winner_value


game = Checkers()
net = CheckersNet(action_size=1024).to(DEVICE)
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_PATH)
if os.path.exists(model_path):
    print(f"Found existing model at {model_path}. Resuming incremental training...")
    net.load_state_dict(torch.load(model_path, map_location=DEVICE, weights_only=True))
else:
    print("No existing model found. Starting training from scratch.")
model = ModelWrapper(net, device=DEVICE)
optimizer = optim.Adam(net.parameters(), lr=0.001, weight_decay=1e-4)
buffer = ReplayBuffer(max_size=10000)

for iteration in range(1, ITERATIONS+1):
    print(f'---------Iteration: {iteration}/{ITERATIONS}---------', flush=True)
    net.eval()

    for episode in range(EPISODES):
        print(f"Processing game: {episode+1}/{EPISODES}...", flush=True)
        history, winner = play_self_play_game(game, model)
        print(f"Game finished. Winner: {winner}, num moves: {len(history)}", flush=True)
        buffer.save_game(history, winner)

    if len(buffer) > BATCH_SIZE:
        print("Training neural network...", flush=True)
        net.train()
        num_batches = 100
        for epoch in range(EPOCHS):
            for _ in range(num_batches):
                states, target_policies, target_values = buffer.sample_batch(BATCH_SIZE)
                states = states.to(DEVICE)
                target_policies = target_policies.to(DEVICE)
                target_values = target_values.to(DEVICE)

                optimizer.zero_grad()
                predicted_policy_logits, predicted_values = net(states)
                value_loss = F.mse_loss(predicted_values, target_values)
                pred_policy_log = F.log_softmax(predicted_policy_logits, dim=1)
                policy_loss = -torch.sum(target_policies * pred_policy_log) / BATCH_SIZE

                total_loss = value_loss + policy_loss
                total_loss.backward()
                optimizer.step()

        print(f"Training finished. Average Loss: {total_loss.item():.4f}", flush=True)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(current_dir, MODEL_PATH)

        torch.save(net.state_dict(), model_path)
        print(f"Model saved to file: {model_path}", flush=True)
