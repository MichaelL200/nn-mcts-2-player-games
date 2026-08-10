import os
import random
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from src.core.models.wrapper import ModelWrapper
from src.core.training.trainer import Trainer, TrainerConfig
from src.games.checkers.checkers import Checkers
import numpy as np
from datetime import timedelta


CONFIG = TrainerConfig(
    episodes=100,
    mcts_time=0.8,
    batch_size=32,
    iterations=50,
    epochs=5,
    num_batches=10,
    max_moves=500,
    explore_rate=1.41,
    learning_rate=0.0001,
    weight_decay=1e-4,
    buffer_size=50000,
    temperature=0.7
)


def setup_distributed():
    if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
        world_size = int(os.environ["WORLD_SIZE"])  # world_size is number of gpus
        rank = int(os.environ["RANK"])  # rank is id in range(world_size)
        local_rank = int(os.environ["LOCAL_RANK"])
        # local rank ranges from 0 to 3 on each server when world_size is 16
        try:
            if torch.cuda.is_available():
                dist.init_process_group(backend="nccl", timeout=timedelta(seconds=7200))
                torch.cuda.set_device(local_rank)
                device = f"cuda:{local_rank}"
            else:
                dist.init_process_group(backend="gloo")
                device = "cpu"
        except Exception as e:
            print(f"Failed to initialize distributed environment: {e}")
            rank = 0
            world_size = 1
            local_rank = 0
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
    else:
        rank = 0
        world_size = 1
        local_rank = 0
        device = "cuda:0" if torch.cuda.is_available() else "cpu"

    return rank, world_size, device, local_rank


if __name__ == "__main__":
    rank, world_size, device, local_rank = setup_distributed()
    # print(f"Running on rank {rank}/{world_size} with device {device}")
    torch.manual_seed(42 + rank)
    np.random.seed(42 + rank)
    random.seed(42 + rank)
    MODEL_PATH = os.path.join("src", "core", "models", "checkers_alphazero_model.pt")
    game = Checkers()
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_PATH)
    model = ModelWrapper.load_or_new(model_path, game.encoder, device=device)
    if torch.cuda.is_available() and world_size > 1:
        model.model = DDP(model.model, device_ids=[local_rank])

    if dist.is_initialized():
        dist.barrier()

    trainer = Trainer(
        game=game,
        model=model,
        model_path=model_path,
        config=CONFIG,
        device=device,
        rank=rank,
        world_size=world_size
    )
    trainer.train()
    if dist.is_initialized():
        dist.destroy_process_group()
