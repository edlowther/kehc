## Link Had-UK climate data with addressbase

### Prerequisites

Create and activate a virtual environment, then install dependencies:

```
python3 -m venv ./kehc-env
source ./kehc-env
python3 -m pip install -r requirements.txt
```

### Data access

This code uses gridded Had-UK data provided by the Centre for Environmental Data Analysis (CEDA) via an FTP server. It's free to access, but requires credentials. 

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

With the virtual environment activated as above, you should now be able to run: 

```
python3 download-annual.py
python3 download-monthly.py
python3 download-daily.py
```

By default, this will transfer data from 1995 to 2022 to the `data` directory in your project folder. It requires approximately 105GB of disk space. 

The variables of interest are average surface temperature (`tas`), minimum surface temperature (`tasmin`) and maximum surface temperature (`tasmax`). All three are available at the annual and monthly resolution; `tasmin` and `tasmax` are available as daily data. 

For more information about the availability of variables in this dataset, please see [the documentation](https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets) on the Met Office website. 
