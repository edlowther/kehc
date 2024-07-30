import os
import sys
import netCDF4
import pandas as pd
import numpy as np

class CollationManager():
    def __init__(self):
        self.years = [2020,2021,2022]
        self.month = self.get_month()
        self.cadence = sys.argv[1]
        self.base_dir = '/home/ccaeelo/Scratch/kehc/'

    def get_month(self):
        if len(sys.argv) > 2:
            month = int(sys.argv[2])
        else:
            month = None
        return month
    
    def get_n_days(self, year, month):
        if year % 4 == 0 and month == 2:
            return 29
        else:
            return int('_ 31 28 31 30 31 30 31 31 30 31 30 31'.split()[month])

    def fp_constructor(self, var, year, month):
        if self.cadence in ['annual', 'monthly']:
            cadence_abbr = self.cadence[:3]
            filename = f'{var}_hadukgrid_uk_1km_{cadence_abbr}_{year}01-{year}12.nc'
        elif self.cadence == 'daily':
            n_days = self.get_n_days(year, month)
            filename = f'{var}_hadukgrid_uk_1km_day_{year}{month:02}01-{year}{month:02}{n_days}.nc'
        return os.path.join(self.base_dir, 'haduk-data', self.cadence, filename)

    def run(self):
        lookup_fp = os.path.join(self.base_dir, 'output', 'lookup.parquet.gzip')
        lookup_df = pd.read_parquet(lookup_fp)
        all_grid_ids = pd.concat([
            lookup_df['grid_id'], 
            lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id']
        ]).drop_duplicates()
        y_x_df = all_grid_ids.str.split('_', expand=True)
        y_x_df.rename(columns={0: 'grid_y', 1: 'grid_x'}, inplace=True)
        if self.cadence == 'annual':
            vars = ['tas', 'tasmin', 'tasmax']
        elif self.cadence == 'monthly': 
            vars = ['tas']
        elif self.cadence == 'daily': 
            vars = ['tasmin', 'tasmax']
        else:
            raise ValueError('`cadence` must be one of annual, monthly or daily')
        for year in self.years:
            output = []
            for var in vars:
                fp = self.fp_constructor(var, year, self.month)
                data = netCDF4.Dataset(fp)
                time = data.variables['time']
                for idx, date in enumerate(netCDF4.num2date(time[:], time.units, time.calendar)):
                    for _, row in y_x_df.iterrows():
                        y = row['grid_y']
                        x = row['grid_x']
                        value = data.variables[var][idx, y, x]
                        if value is np.ma.masked:
                            value = np.nan
                        grid_id = f'{y}_{x}'
                        output.append({
                            'date': str(date),
                            'cadence': self.cadence,
                            'var_name': var,
                            'value': value,
                            'grid_id': grid_id,
                            'latitude': data.variables['latitude'][y, x],
                            'longitude': data.variables['longitude'][y, x]
                        })
            
            haduk_df = pd.DataFrame(output)
            if self.cadence == 'daily':
                filename = f'{self.cadence}_{year}_{self.month:02}_df.csv'
            else:
                filename = f'{self.cadence}_{year}_df.csv'
            output_fp = os.path.join(self.base_dir, 'in_progress', filename)
            haduk_df.to_csv(output_fp, index=False)

collation_manager = CollationManager()
collation_manager.run()
