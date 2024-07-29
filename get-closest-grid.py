import sys
import netCDF4
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

STRIDE = 10000
idx = int(sys.argv[1]) * STRIDE

# Arbitrary choice of .nc file - loading just for lat/lon, not for tas:
data = netCDF4.Dataset('/home/ccaeelo/Scratch/kehc/haduk-data/annual/tas_hadukgrid_uk_1km_ann_200201-200212.nc')
haduk_lats = data.variables['latitude'][:]
haduk_lons = data.variables['longitude'][:]

haduk_grid_points = np.stack((haduk_lats.flatten(), haduk_lons.flatten()), axis=-1)
haduk_grid_points = np.deg2rad(haduk_grid_points)
tree = BallTree(haduk_grid_points, leaf_size=30, metric='haversine')

tas = data.variables['tas']

london_df = pd.read_csv('/home/ccaeelo/Scratch/kehc/london_df.csv')

rows = []

for _, row in london_df[idx-STRIDE:idx].iterrows():
    uprn = row['uprn']
    abp_lat = row['latitude']
    abp_lon = row['longitude']

    _, closest_idxs = tree.query(np.deg2rad([[row['latitude'], row['longitude']]]), k=9)
    k_idx = 0
    closest_y, closest_x = np.unravel_index(closest_idxs[0][k_idx], data.variables['longitude'].shape)

    # dist_sq = (haduk_lats - abp_lat)**2 + (haduk_lons - abp_lon)**2
    # closest_y, closest_x = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)

    row = {
        'uprn': int(uprn), 
        'grid_x': closest_x,
        'grid_y': closest_y
    }
    is_masked = tas[0, closest_y, closest_x] is np.ma.masked
    row['is_masked'] = is_masked
    while is_masked:
        k_idx += 1
        closest_y, closest_x = np.unravel_index(closest_idxs[0][k_idx], data.variables['longitude'].shape)
        is_masked = tas[0, closest_y, closest_x] is np.ma.masked
        row['unmasked_grid_x'] = closest_x
        row['unmasked_grid_y'] = closest_y

    rows.append(row)

output_df = pd.DataFrame(rows)
output_df.to_csv(f'/home/ccaeelo/Scratch/kehc/london_dfs-haversine/lookup_{idx:07}.csv', index=False)
