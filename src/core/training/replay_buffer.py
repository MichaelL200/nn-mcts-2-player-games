import random
import torch
import numpy as np
from collections import deque


class ReplayBuffer:
    def __init__(self, max_size=10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)

    def save_game(self, game_history, winner_id):
        for state_tensor, policy_vector, player in game_history:
            if winner_id == 0:
                z = 0.0
            else:
                z = 1.0 if player.value == winner_id else -1.0

            self.buffer.append((state_tensor.cpu(), policy_vector, z))

    def sample_batch(self, batch_size):
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        states, policies, values = zip(*batch)

        states_tensor = torch.cat(states)
        policies_tensor = torch.tensor(np.array(policies), dtype=torch.float32)
        values_tensor = torch.tensor(np.array(values), dtype=torch.float32).unsqueeze(1)

        return states_tensor, policies_tensor, values_tensor

    def __len__(self):
        return len(self.buffer)
