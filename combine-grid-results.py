import os
import pandas as pd
import numpy as np

lookup_dfs = []

base_dir = '/home/ccaeelo/Scratch/kehc/england_dfs'
for filename in os.listdir(base_dir):
    if filename != '.gitkeep':
        fp = os.path.join(base_dir, filename)
        try:
            lookup_dfs.append(pd.read_csv(fp))
        except Exception as e:
            print(e)

lookup_df = pd.concat(lookup_dfs)
lookup_df['grid_id'] = lookup_df['grid_y'].astype(str) + '_' + lookup_df['grid_x'].astype(str)
# lookup_df['unmasked_grid_id'] = lookup_df['unmasked_grid_y'].astype(int).astype(str) + '_' + lookup_df['unmasked_grid_x'].astype(int).astype(str)
lookup_df['unmasked_grid_id'] = lookup_df.apply(
    lambda row: f"{int(row['unmasked_grid_y'])}_{int(row['unmasked_grid_x'])}" if row['is_masked'] else None, 
    axis='columns'
)
lookup_df[['uprn', 'grid_id', 'is_masked', 'unmasked_grid_id']].to_parquet('/home/ccaeelo/Scratch/kehc/output/lookup.parquet.gzip', compression='gzip', index=False)
