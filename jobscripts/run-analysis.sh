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

# module unload gcc-libs
# module load gdal/3.1.3/gnu-9.2.0
# source kehc-env/bin/activate
module load python/miniconda3/24.3.0-0
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
conda activate kehc
TASK_ID=$(sed -n "${SGE_TASK_ID}p" tasks.txt)
python get-closest-grid.py $TASK_ID
