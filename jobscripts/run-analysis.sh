#!/bin/bash -l

# Example jobscript to run a single core R job

# Request ten minutes of wallclock time (format hours:minutes:seconds).
# Change this to suit your requirements.
#$ -l h_rt=23:0:0

#$ -l mem=4G
#$ -pe smp 1
#$ -t 1:518

# Set the name of the job. You can change this if you wish.
#$ -N kehc-array

#$ -e /home/ccaeelo/Scratch/kehc/logs/error.txt
#$ -o /home/ccaeelo/Scratch/kehc/logs/out.txt

# Set the working directory to somewhere in your scratch space.  This is
# necessary because the compute nodes cannot write to your $HOME
# NOTE: this directory must exist.
# Replace "<your_UCL_id>" with your UCL user ID
#$ -wd /home/ccaeelo/Scratch/kehc
# export R_LIBS=/home/ccaeelo/Scratch/libs:$R_LIBS
# export LD_LIBRARY_PATH=/home/ccaeelo/Scratch/.rpackages/lib:$LD_LIBRARY_PATH

# Your work must be done in $TMPDIR (serial jobs particularly) 
# cd $TMPDIR

# Load the R module and run your R program
module unload gcc-libs
module load gdal/3.1.3/gnu-9.2.0
source kehc-env/bin/activate
python get-closest-grid.py $SGE_TASK_ID

# R --no-save < /home/ccaeelo/Scratch/EuroCORDEX-UK-projections/UKTempPrecip_Specimen.r > cordex-parallel.out

# Preferably, tar-up (archive) all output files to transfer them back 
# to your space. This will include the R_output file above.
# tar zcvf $HOME/Scratch/EuroCORDEX-UK-projections/output-files/$JOB_ID.tgz $TMPDIR

# Make sure you have given enough time for the copy to complete!
