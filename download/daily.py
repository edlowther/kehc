import os
from ftplib import FTP
from dotenv import load_dotenv
load_dotenv()

client = FTP('ftp.ceda.ac.uk', os.environ['USERNAME'], os.environ['PASSWORD'])
for var in ['tasmin', 'tasmax']:
    print(var)
    for year in range(1995, 2023):
        print(year)
        for month in range(1,13):
            print(f'  {month:02}')
            # Handle leap years:
            if year % 4 == 0 and month == 2:
                ndays = 29
            else:
                ndays = int('_ 31 28 31 30 31 30 31 31 30 31 30 31'.split()[month])
            # Move to correct location on FTP server:
            client.cwd(f'/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.2.0.ceda/1km/{var}/day/v20230328/')
            # Define data source and destination:
            filename = f'{var}_hadukgrid_uk_1km_day_{year}{month:02}01-{year}{month:02}{ndays}.nc'
            dest = f'./haduk-data/daily/{filename}'
            # Download data:
            with open(dest, 'wb') as f:
                client.retrbinary(f'RETR {filename}', f.write)

# Close FTP connection:
client.close()
