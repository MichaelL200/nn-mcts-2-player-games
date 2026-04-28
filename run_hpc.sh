#!/bin/bash
#SBATCH -A plggolemml26-gpu-a100
#SBATCH -p plgrid-gpu-a100       
#SBATCH --nodes=1             
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/slurm_%j.log

module load Miniconda3/4.9.2
eval "$(conda shell.bash hook)"
source activate /net/tscratch/people/$USER/env_checkers
python -m torch.distributed.run --nproc_per_node=4 train.py