#!/bin/bash -l

#$ -l h_rt=0:59:0
#$ -l mem=2G
#$ -pe smp 1
#$ -N collate-nc-head

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module load python/miniconda3/24.3.0-0
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
conda activate kehc

qsub jobscripts/collation-helper.sh 

# python collate/collation-manager.py annual
# python collate/collation-manager.py monthly
