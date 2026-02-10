import os
import sys
import pandas as pd
from pathlib import Path

base_dir = Path('/home/ccaeelo/Scratch/kehc')
in_progress = base_dir / 'in_progress'
output = base_dir / 'output'

for cadence in ['daily', 'monthly', 'annual']:
    if cadence == 'daily':
        STRIDE = 5
        start_years = [2005, 2010, 2015, 2020]
        year = start_years[int(sys.argv[1]) - 1]
        print(year)
        window = range(year, year+STRIDE)
        parent = output / cadence / f'{year}_{year+STRIDE-1}' if year < 2020 else output / f'{year}_{year+2}'
        parent.mkdir(parents=True, exist_ok=True)
        dfs = []
        for filename in os.listdir(in_progress / cadence):
            if '.csv' in filename:
                filename_year = int(filename.split('_')[1])
                if filename_year in window:
                    print(filename)
                    tmp_df = pd.read_csv(in_progress / cadence / filename, 
                                         dtype={'grid_id': 'str', 'var_name': 'str', 'date': 'str', 'value': 'float64'},
                                        usecols=['grid_id', 'var_name', 'date', 'value'])
                    dfs.append(tmp_df)
        output_df = pd.concat(dfs)
        for var_name in ['tasmin', 'tasmax']:
            output_df.loc[
                output_df['var_name'] == var_name
            ].sort_values(by='grid_id').to_parquet(parent / f'{var_name}.parquet.gzip', compression='gzip', index=False)
    else:
        parent = output / cadence
        parent.mkdir(parents=True, exist_ok=True)
        dfs = []
        for filename in os.listdir(in_progress / cadence):
            if '.csv' in filename:
                    print(filename)
                    tmp_df = pd.read_csv(in_progress / cadence / filename, 
                                         dtype={'grid_id': 'str', 'var_name': 'str', 'date': 'str', 'value': 'float64'},
                                        usecols=['grid_id', 'var_name', 'date', 'value'])
                    dfs.append(tmp_df)
        output_df = pd.concat(dfs)
        output_df.sort_values(by=['grid_id', 'var_name', 'date']).to_parquet(parent / 'tas_tasmin_tasmax.parquet.gzip', compression='gzip', index=False)
        
