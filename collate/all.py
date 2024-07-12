import os
import pandas as pd

base_dir = '/home/ccaeelo/Scratch/kehc/in_progress/'

dfs = []

for filename in os.listdir(base_dir):
    dfs.append(pd.read_csv(os.path.join(base_dir, filename)))

output_df = pd.concat(dfs)
output_vars = ['grid_id', 'date', 'cadence', 'var_name', 'value']
output_df[output_vars].to_parquet('/home/ccaeelo/Scratch/kehc/output/output.parquet.gzip', compression='gzip', index=False)
