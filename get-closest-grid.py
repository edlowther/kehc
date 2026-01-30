import sys
import netCDF4
import numpy as np
import pandas as pd

STRIDE = 100000
idx = int(sys.argv[1]) * STRIDE

# Arbitrary choice of .nc file - loading just for lat/lon, and whether `tas` is masked, not actual `tas` values:
data = netCDF4.Dataset('/home/ccaeelo/Scratch/kehc/haduk-data/daily/tasmax_hadukgrid_uk_1km_day_20050101-20050131.nc')
haduk_Ys = data.variables['projection_y_coordinate'][:]
haduk_Xs = data.variables['projection_x_coordinate'][:]

tas = data.variables['tasmax']

england_df = pd.read_csv('/home/ccaeelo/Scratch/kehc/england_df.csv')

rows = []

for _, row in england_df[idx-STRIDE:idx].iterrows():
    uprn = row['uprn']
    abp_Y = row['Y']
    abp_X = row['X']

    dists_sq_y = (haduk_Ys - abp_Y)**2
    dists_sq_x = (haduk_Xs - abp_X)**2

    closest_y = np.argmin(dists_sq_y)
    closest_x = np.argmin(dists_sq_x)

    row = {
        'uprn': int(uprn), 
        'grid_x': closest_x,
        'grid_y': closest_y
    }
    is_masked = tas[0, closest_y, closest_x] is np.ma.masked
    row['is_masked'] = is_masked

    if is_masked:
        dist_mesh = np.array([[dist_sq_y + dist_sq_x for dist_sq_x in dists_sq_x] for dist_sq_y in dists_sq_y])

    while is_masked:
        dist_mesh[closest_y, closest_x] = np.inf

        closest_y, closest_x = np.unravel_index(np.argmin(dist_mesh), dist_mesh.shape)

        is_masked = tas[0, closest_y, closest_x] is np.ma.masked
        row['unmasked_grid_x'] = closest_x
        row['unmasked_grid_y'] = closest_y

    rows.append(row)

output_df = pd.DataFrame(rows)
output_df.to_csv(f'/home/ccaeelo/Scratch/kehc/england_dfs/lookup_{idx:010}.csv', index=False)
