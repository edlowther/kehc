import sys
import netCDF4
import numpy as np
import pandas as pd

STRIDE = 10000
idx = int(sys.argv[1]) * STRIDE

# Arbitrary choice of .nc file - loading just for lat/lon, not for tas:
data = netCDF4.Dataset('/home/ccaeelo/Scratch/kehc/haduk-data/annual/tas_hadukgrid_uk_1km_ann_200201-200212.nc')
haduk_lats = data.variables['latitude'][:]
haduk_lons = data.variables['longitude'][:]

london_df = pd.read_csv('/home/ccaeelo/Scratch/kehc/london_df.csv')

rows = []

for _, row in london_df[idx-STRIDE:idx].iterrows():
    uprn = row['uprn']
    abp_lat = row['latitude']
    abp_lon = row['longitude']

    dist_sq = (haduk_lats - abp_lat)**2 + (haduk_lons - abp_lon)**2
    closest_y, closest_x = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)

    rows.append({
        'uprn': int(uprn), 
        'grid_x': closest_x,
        'grid_y': closest_y
    })

output_df = pd.DataFrame(rows)
print(output_df.shape)
output_df.to_csv(f'/home/ccaeelo/Scratch/kehc/london_dfs/lookup_{idx:07}.csv', index=False)
