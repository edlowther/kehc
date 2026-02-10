#!/bin/bash -l

#$ -l h_rt=5:59:0
#$ -l mem=40G
#$ -pe smp 1
#$ -t 1:4
#$ -N group-and-output

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module load python/miniconda3/24.3.0-0
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
conda activate kehc
python collate/all.py $SGE_TASK_ID
