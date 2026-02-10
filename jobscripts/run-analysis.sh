#!/bin/bash -l

#$ -l h_rt=1:30:0
#$ -l mem=2G
#$ -pe smp 1
#$ -t 1:23
#$ -N kehc-array

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module load python/miniconda3/24.3.0-0
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
conda activate kehc

# Useful method for hoovering up failed tasks:
# TASK_ID=$(sed -n "${SGE_TASK_ID}p" tasks.txt)
# python get-closest-grid.py $TASK_ID

# Otherwise for standard processing, match -t flag with required number of files:
python get-closest-grid.py $SGE_TASK_ID

