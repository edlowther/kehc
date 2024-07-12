import os
import pandas as pd

lookup_dfs = []

base_dir = '/home/ccaeelo/Scratch/kehc/london_dfs'
for filename in os.listdir(base_dir):
    fp = os.path.join(base_dir, filename)
    try:
        lookup_dfs.append(pd.read_csv(fp))
    except Exception as e:
        print(e)

lookup_df = pd.concat(lookup_dfs)
lookup_df['grid_id'] = lookup_df['grid_y'].astype(str) + '_' + lookup_df['grid_x'].astype(str)
lookup_df[['uprn', 'grid_id']].to_parquet('/home/ccaeelo/Scratch/kehc/output/lookup.parquet.gzip', compression='gzip', index=False)
