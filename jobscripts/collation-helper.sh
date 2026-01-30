#!/bin/bash -l

#$ -l h_rt=11:59:0
#$ -l mem=40G
#$ -pe smp 1
#$ -t 1:12
#$ -N collate-nc-helper-array

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module load python/miniconda3/24.3.0-0
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
conda activate kehc
python collate/collation-manager.py daily $SGE_TASK_ID
