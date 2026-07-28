import torch.nn as nn
import torch.nn.functional as F


class ResBlock(nn.Module):
    def __init__(self, num_hidden):
        super().__init__()
        self.conv1 = nn.Conv2d(num_hidden, num_hidden, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(num_hidden)
        self.conv2 = nn.Conv2d(num_hidden, num_hidden, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(num_hidden)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x += residual
        x = F.relu(x)
        return x


class GameNet(nn.Module):
    def __init__(self, board_rows=10, board_cols=10, action_size=2500, num_res_blocks=4, num_hidden=64, in_channels=5):
        super().__init__()
        self.board_rows = board_rows
        self.board_cols = board_cols
        self.action_size = action_size

        self.start_block = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=num_hidden, kernel_size=3, padding=1),
            nn.BatchNorm2d(num_hidden),
            nn.ReLU()
        )

        self.backbone = nn.ModuleList([ResBlock(num_hidden) for _ in range(num_res_blocks)])

        self.policy_head = nn.Sequential(
            nn.Conv2d(num_hidden, 2, kernel_size=1),
            nn.BatchNorm2d(2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * board_rows * board_cols, action_size))

        self.value_head = nn.Sequential(
            nn.Conv2d(num_hidden, 1, kernel_size=1),
            nn.BatchNorm2d(1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(1 * board_rows * board_cols, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.start_block(x)
        for res_block in self.backbone:
            x = res_block(x)

        policy_logits = self.policy_head(x)
        value = self.value_head(x)

        return policy_logits, value
