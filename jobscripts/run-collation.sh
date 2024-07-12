#!/bin/bash -l

#$ -l h_rt=0:59:0
#$ -l mem=2G
#$ -pe smp 1
#$ -N collate-nc-head

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

#$ -wd /home/ccaeelo/Scratch/kehc
# cd $TMPDIR

module unload gcc-libs
module load gdal/3.1.3/gnu-9.2.0
source kehc-env/bin/activate

qsub jobscripts/collation-helper.sh 

python collate/collation-manager.py annual
python collate/collation-manager.py monthly
