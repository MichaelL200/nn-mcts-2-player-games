import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from src.core.models.wrapper import ModelWrapper
from src.core.training.trainer import Trainer, TrainerConfig
from src.games.checkers.checkers import Checkers


CONFIG = TrainerConfig(
    episodes=5,
    mcts_time=0.5,
    batch_size=64,
    iterations=1,
    epochs=1,
    num_batches=100,
    max_moves=50,
    explore_rate=1.41,
    learning_rate=0.001,
    weight_decay=1e-4,
    buffer_size=10000,
)

def setup_distributed():
    if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
        world_size = int(os.environ["WORLD_SIZE"])# world_size is number of gpus
        rank = int(os.environ["RANK"])# rank is id in range(world_size)
        local_rank = int(os.environ["LOCAL_RANK"])# local rank when i have world_size 16 and 4 servers local rank will me range(0,4) in each server
    else:
        rank = 0
        world_size = 1
        local_rank = 0

    if torch.cuda.is_available():
        dist.init_process_group(backend="nccl")
        torch.cuda.set_device(local_rank)
        device = f"cuda:{local_rank}"
    else:
        dist.init_process_group(backend="gloo")
        device = "cpu"
        
    return rank, world_size, device, local_rank
if __name__ == "__main__":
    rank, world_size, device,local_rank = setup_distributed()
    #print(f"Running on rank {rank}/{world_size} with device {device}")
    torch.manual_seed(42 + rank)
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