## Link Had-UK climate data with addressbase

### Prerequisites

The code on this page was designed to run on UCL's Myriad HPC system (with one exception, described below), where the recommended tool for working with python dependencies is `venv`, so we begin by creating and activating a virtual environment as follows:

```
python3 -m venv ./kehc-env
source ./kehc-env
python3 -m pip install -r requirements.txt
```

### Data access

We need gridded Had-UK data provided by the Centre for Environmental Data Analysis (CEDA) via an FTP server. It's free to access, but requires credentials. 

First, create a general CEDA account: 
https://services.ceda.ac.uk/cedasite/register/info/

Then, once logged in, go to the [MyCeda](https://services.ceda.ac.uk/cedasite/myceda?_ga=2.196270316.1731834615.1716882715-284125426.1716479512) page and click on "Configure FTP Account" to get an FTP password. 

Create a text file called `.env` in the project's root directory and save your general CEDA username and FTP password (NB not the general CEDA password) in this file as follows:

```
USERNAME=<YOUR_USERNAME>
PASSWORD=<YOUR_FTP_PASSWORD>
```

For more information, please see the [data documentation](https://catalogue.ceda.ac.uk/uuid/46f8c1377f8849eeb8570b8ac9b26d86) and [FTP server documentation](https://help.ceda.ac.uk/article/280-ftp).

### Download the data

With the virtual environment activated as described above, you should now be able to run: 

```
python3 download/annual.py
python3 download/monthly.py
python3 download/daily.py
```

By default, this will transfer data from 1995 to 2022 to the `haduk-data` directory in your project folder. It requires approximately 105GB of disk space. 

The variables of interest are average surface temperature (`tas`), minimum surface temperature (`tasmin`) and maximum surface temperature (`tasmax`). All three are available at the annual and monthly resolution; `tasmin` and `tasmax` are available as daily data. 

For more information about the availability of variables in this dataset, please see [the documentation](https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets) on the Met Office website. 

### Define geography of interest

In our test case, we're interested in analysing data for London, so before we do anything else we're going to need to define what we mean by London; some python code to generate this is available [here](./utils/get-london-outline.py) - the output of this code is availalbe in the `shp` directory. 

*Copyright notice: the source for this shapefile is Office for National Statistics licensed under the Open Government Licence v.3.0. Contains OS data © Crown copyright and database right 2024.* 

### Filtering addressbase

Having generated/downloaded the shapefile described above, we're going to use a command-line tool called `ogr2ogr` - one of many useful features of the open-source `gdal` software library - to filter our copy of the addressbase premium data, which we have in the geopackage (`gpkg`) format and we assume has been placed in the root directory of this project. 

It turns out to be non trivial to use `ogr2ogr` on Myriad, due to its dependeny on `GEOS`, although it may be possible to `module load geos` then compile `gdal` from source, configured to point to the location of `GEOS` on the system. 

You may prefer to run this section on a different system, possibly your laptop, using the conda package manager to install `gdal` and its dependencies:
```
conda create -n gdal
conda activate gdal
conda install conda-forge::gdal
```

In the addressbase premium geopackage, the `e105_abprem_e_blpu` layer is the one that contains geospatial information: we use it to select the latitude and longitude of each uprn in London and save as a `csv` file as follows: 

```
ogr2ogr -select uprn,latitude,longitude -lco GEOMETRY=AS_XY -f 'CSV' ./london_df.csv -clipsrc ./shp/london.shp e105_ABPrem_Eng.gpkg e105_abprem_e_blpu
```

### Finding closest grid cells

It's computationally expensive to find the closest grid cell for each uprn in the addressbase data - even the filtered, London-only version defined above. However, the task can be divided up into many small batches and worked on in parallel. This is where Myriad really comes into its own. 

Based on the number of lines in the `london_df.csv` file output above (using `wc`), we can tell there are 5,178,347 uprns in the data for London. This means we can split the task up into 518 jobs which will process 10,000 uprns each (defined as `STRIDE` in `get-closest-grid.py`), with the final task tackling the remainder of 8,347. To do this we define an array job on Myriad with 518 separate tasks (`#$ -t 1:518`), each requesting a relatively small amount of virtual memory and just one CPU. 

This can be submitted on SGE using `qsub jobscripts/run-analysis.sh`. Because each of the 518 tasks outputs its own csv file in the `london_dfs` directory we can then bring them together into one compressed parquet file using `python combine-grid-results.py` with the virtual environment activated as ever. 

### Data extraction from netCDF

Finally, we need to bring together the Had-UK climate data for each of the closest grid cells to our London uprns. This is somewhat computationally expensive, mainly for the daily data, so we submit a job to SGE for this as well - `./jobscripts/run-collation.sh` - which makes use of a helper class `./collate/collation-manager.py`, where you can define which years of data you'd like to download the data for in the `self.years` attribute of the `CollationManager`. Use a list of integers for this (for just one year, set the list to be of length one). 

On Myriad, this job will submit a further array of jobs to process the daily data in parallel (one task for each month). This is codified in `jobscripts/collation-helper.sh`. 

Once all of the above tasks are complete, run `python collate/all.py` to bring all of this data together and save it out as `./output/output.parquet.gzip`. 

### Tests

[TODO]
