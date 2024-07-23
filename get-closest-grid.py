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
tas = data.variables['tas']

london_df = pd.read_csv('/home/ccaeelo/Scratch/kehc/london_df.csv')

rows = []

for _, row in london_df[idx-STRIDE:idx].iterrows():
    uprn = row['uprn']
    abp_lat = row['latitude']
    abp_lon = row['longitude']

    dist_sq = (haduk_lats - abp_lat)**2 + (haduk_lons - abp_lon)**2
    closest_y, closest_x = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)

    row = {
        'uprn': int(uprn), 
        'grid_x': closest_x,
        'grid_y': closest_y
    }
    is_masked = tas[0, closest_y, closest_x] is np.ma.masked
    row['is_masked'] = is_masked
    while is_masked:
        dist_sq[closest_y, closest_x] = 999999999
        closest_y, closest_x = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)
        is_masked = tas[0, closest_y, closest_x] is np.ma.masked
        row['unmasked_grid_x'] = closest_x
        row['unmasked_grid_y'] = closest_y

    rows.append(row)

output_df = pd.DataFrame(rows)
print(output_df.shape)
output_df.to_csv(f'/home/ccaeelo/Scratch/kehc/london_dfs/lookup_{idx:07}.csv', index=False)
