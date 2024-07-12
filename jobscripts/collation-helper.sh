#!/bin/bash -l

#$ -l h_rt=1:59:0
#$ -l mem=2G
#$ -pe smp 1
#$ -t 1:12
#$ -N collate-nc-helper-array

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module unload gcc-libs
module load gdal/3.1.3/gnu-9.2.0
source kehc-env/bin/activate
python collate/collation-manager.py daily $SGE_TASK_ID
