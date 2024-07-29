import math
import pytest
import pandas as pd
import numpy as np
import netCDF4 
from shapely.geometry import Point
from geopandas import GeoSeries

lookup_df = pd.read_parquet('~/Scratch/kehc/output/lookup.parquet.gzip')
output_df = pd.read_parquet('~/Scratch/kehc/output/output.parquet.gzip')
years_present_in_output_data = output_df['date'].str[:4].unique().astype(int)
n_years = len(years_present_in_output_data)
n_samples = 10000
half_grid_length = 500
grid_hypotenuse = math.sqrt(half_grid_length**2 + half_grid_length**2)
tolerance_in_m = 10

london_df = pd.read_csv('./london_df.csv')

def test_all_uprns_have_grid_id():
    assert pd.isna(lookup_df['grid_id']).sum() == 0

def test_all_uprns_with_masked_grids_have_alternative_grid_id():
    assert pd.isna(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id']).sum() == 0

def test_all_uprns_with_unmasked_grids_do_not_have_alternative_grid_id():
    assert all(pd.isna(lookup_df.loc[~lookup_df['is_masked'], 'unmasked_grid_id']))

def test_all_uprns_are_unique():
    assert len(lookup_df['uprn']) == len(lookup_df['uprn'].unique())

def test_all_grid_ids_are_in_output_haduk_data():
    print(np.setdiff1d(lookup_df['grid_id'], output_df['grid_id']))
    print(np.setdiff1d(output_df['grid_id'], lookup_df['grid_id']))
    assert all(lookup_df['grid_id'].isin(output_df['grid_id']))
    assert all(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id'].isin(output_df['grid_id']))

def test_all_masked_grids_are_NAs_in_output_haduk_data():
    assert all(pd.isna(lookup_df.loc[lookup_df['is_masked']].merge(output_df, on='grid_id')['value']))

def test_no_unmasked_grids_are_NAs_in_output_haduk_data():
    assert pd.isna(lookup_df.loc[lookup_df['is_masked']].merge(output_df, left_on='unmasked_grid_id', right_on='grid_id')['value']).sum() == 0

def test_expected_number_of_annual_data_points_found():
    cadence_df = output_df.loc[output_df['cadence'] == 'annual']
    assert all(cadence_df.groupby(['grid_id', 'var_name'])['var_name'].count() == n_years)

def test_expected_number_of_monthly_data_points_found():
    cadence_df = output_df.loc[output_df['cadence'] == 'monthly']
    assert all(cadence_df.groupby(['grid_id', 'var_name'])['var_name'].count() == n_years * 12)

def test_expected_number_of_daily_data_points_found():
    cadence_df = output_df.loc[output_df['cadence'] == 'daily']
    leap_year_count = 0
    for year in years_present_in_output_data:
        if year % 4 == 0:
            leap_year_count += 1
    assert all(cadence_df.groupby(['grid_id', 'var_name'])['var_name'].count() == (n_years - leap_year_count) * 365 + leap_year_count * 366)

def test_random_sample_of_annual_output_data_matches_source():
    sample_df = output_df.loc[(~pd.isna(output_df['value'])) & (output_df['cadence'] == 'annual')].sample(n_samples)
    for _, row in sample_df.iterrows():
        y, x = row['grid_id'].split('_')
        var = row['var_name']
        year = row['date'][:4]
        data = netCDF4.Dataset(f'/home/ccaeelo/Scratch/kehc/haduk-data/annual/{var}_hadukgrid_uk_1km_ann_{year}01-{year}12.nc')
        assert row['value'] == pytest.approx(data.variables[var][0, y, x])

def test_random_sample_of_monthly_output_data_matches_source():
    sample_df = output_df.loc[(~pd.isna(output_df['value'])) & (output_df['cadence'] == 'monthly')].sample(n_samples)
    for _, row in sample_df.iterrows():
        y, x = row['grid_id'].split('_')
        var = row['var_name']
        year = row['date'][:4]
        month_idx = int(row['date'][5:7]) - 1
        data = netCDF4.Dataset(f'/home/ccaeelo/Scratch/kehc/haduk-data/monthly/{var}_hadukgrid_uk_1km_mon_{year}01-{year}12.nc')
        assert row['value'] == pytest.approx(data.variables[var][month_idx, y, x])

def test_random_sample_of_daily_output_data_matches_source():
    sample_df = output_df.loc[(~pd.isna(output_df['value'])) & (output_df['cadence'] == 'daily')].sample(n_samples)
    for _, row in sample_df.iterrows():
        y, x = row['grid_id'].split('_')
        var = row['var_name']
        year = int(row['date'][:4])
        month = int(row['date'][5:7])
        day_idx = int(row['date'][8:10]) - 1
        if year % 4 == 0 and month == 2:
            n_days = 29
        else:
            n_days = int('_ 31 28 31 30 31 30 31 31 30 31 30 31'.split()[month])
        data = netCDF4.Dataset(f'/home/ccaeelo/Scratch/kehc/haduk-data/daily/{var}_hadukgrid_uk_1km_day_{year}{month:02}01-{year}{month:02}{n_days}.nc')
        assert row['value'] == pytest.approx(data.variables[var][day_idx, y, x])

def test_random_sample_of_unmasked_uprns_are_within_expected_distance_of_grid_cell():
    sample_df = lookup_df.loc[~lookup_df['is_masked']].sample(n_samples)
    sample_df = sample_df.merge(london_df, on='uprn')
    data = netCDF4.Dataset(f'/home/ccaeelo/Scratch/kehc/haduk-data/monthly/tas_hadukgrid_uk_1km_mon_200201-200212.nc')
    uprn_points = []
    grid_points = []
    for _, row in sample_df.iterrows():
        uprn_points.append(Point(float(row['longitude']), float(row['latitude'])))
        y, x = row['grid_id'].split('_')
        grid_points.append(Point(data.variables['longitude'][y, x], data.variables['latitude'][y, x]))
    uprn_points = GeoSeries(uprn_points, crs='EPSG:4326').to_crs('EPSG:27700')
    grid_points = GeoSeries(grid_points, crs='EPSG:4326').to_crs('EPSG:27700')
    assert all(uprn_points.distance(grid_points) < grid_hypotenuse + tolerance_in_m)

def test_all_masked_uprns_are_between_bounds_of_expected_distance_of_grid_cell():
    tmp_df = lookup_df.loc[lookup_df['is_masked']]
    tmp_df = tmp_df.merge(london_df, on='uprn')
    data = netCDF4.Dataset(f'/home/ccaeelo/Scratch/kehc/haduk-data/monthly/tas_hadukgrid_uk_1km_mon_200201-200212.nc')
    uprn_points = []
    grid_points = []
    for _, row in tmp_df.iterrows():
        uprn_points.append(Point(float(row['longitude']), float(row['latitude'])))
        y, x = row['unmasked_grid_id'].split('_')
        grid_points.append(Point(data.variables['longitude'][y, x], data.variables['latitude'][y, x]))
    uprn_points = GeoSeries(uprn_points, crs='EPSG:4326').to_crs('EPSG:27700')
    grid_points = GeoSeries(grid_points, crs='EPSG:4326').to_crs('EPSG:27700')
    dists = uprn_points.distance(grid_points)
    assert all(dists > half_grid_length - tolerance_in_m)
    assert all(dists < grid_hypotenuse * 2 + tolerance_in_m)
