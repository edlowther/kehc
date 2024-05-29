import os
from ftplib import FTP
from dotenv import load_dotenv
load_dotenv()

client = FTP('ftp.ceda.ac.uk', os.environ['USERNAME'], os.environ['PASSWORD'])
for var in ['tas', 'tasmin', 'tasmax']:
    print(var)
    for year in range(1995, 2023):
        print(year)
        # Move to correct location on FTP server:
        client.cwd(f'/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.2.0.ceda/1km/{var}/ann/v20230328/')
        # Define data source and destination:
        filename = f'{var}_hadukgrid_uk_1km_ann_{year}01-{year}12.nc'
        dest = f'./data/annual/{filename}'
        # Download data:
        with open(dest, 'wb') as f:
            client.retrbinary(f'RETR {filename}', f.write)

# Close FTP connection
client.close()
