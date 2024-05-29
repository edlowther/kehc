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

### Download the data

With the virtual environment activated as above, you should now be able to run: 

```
python3 download-annual.py
python3 download-monthly.py
python3 download-daily.py
```

By default, this will transfer data from 1995 to 2022 to the `data` directory in your project folder. It requires approximately 105GB of disk space. 
