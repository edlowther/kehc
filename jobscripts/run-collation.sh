#!/bin/bash -l

#$ -l h_rt=4:59:0
#$ -l mem=20G
#$ -pe smp 1
#$ -t 1:16
#$ -N collate-nc-head

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module load python/miniconda3/24.3.0-0
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
conda activate kehc

# Uncomment for daily and remove -t flag:
# qsub jobscripts/collation-helper.sh 
# Uncomment for annual and remove -t flag:
# python collate/collation-manager.py annual
# For monthly, requires a -t value (task id) for each input year:
python collate/collation-manager.py monthly $SGE_TASK_ID
