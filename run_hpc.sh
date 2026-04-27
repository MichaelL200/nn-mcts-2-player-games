#!/bin/bash
#SBATCH -A plggolemml26-gpu-a100
#SBATCH -p plgrid-gpu-a100       
#SBATCH --nodes=1             
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/slurm_%j.log

module load Miniconda3/4.9.2
source activate /net/tscratch/people/$USER/env_checkers
torchrun --nproc_per_node=1 train.py