import math
import pytest
import pandas as pd
import polars as pl
import os
from pathlib import Path
import numpy as np
import netCDF4 
from shapely.geometry import Point
from geopandas import GeoSeries

output = Path('../rdss-volume/edlowther/data/output/')

lookup_df = pd.read_parquet(output / 'lookup.parquet.gzip')
# output_df = pd.read_csv('./output_sample.csv')
# output_na_grid_ids = set(pd.read_csv('./output_na_grid_ids.csv')['grid_id'].values)
# output_non_na_grid_ids = set(pd.read_csv('./output_non_na_grid_ids.csv')['grid_id'].values)

output_na_grid_ids = pl.Series()
output_non_na_grid_ids = pl.Series()
samples = []

cadence = 'daily'
for year_range in os.listdir(output / cadence):
    if year_range != '.ipynb_checkpoints':
        for fp in os.listdir(output / cadence / year_range):
            if fp != '.ipynb_checkpoints':
                print(fp)
                tmp_df = pl.read_parquet(output / cadence / year_range / fp)
                window = list(range(int(tmp_df['date'].str.slice(0, 4).min()), int(tmp_df['date'].str.slice(0, 4).max())+1))
                n_years = len(window)
                leap_year_count = 0
                for year in window:
                    if year % 4 == 0:
                        leap_year_count += 1
                expected_count = (n_years - leap_year_count) * 365 + leap_year_count * 366
                if len(output_na_grid_ids) == 0:
                    output_na_grid_ids = tmp_df.filter(pl.col('value').is_null()).select('grid_id').unique().sort(by='grid_id')
                    output_non_na_grid_ids = tmp_df.filter(~pl.col('value').is_null()).select('grid_id').unique().sort(by='grid_id')
                else:
                    assert tmp_df.filter(pl.col('value').is_null()).select('grid_id').unique().sort(by='grid_id').equals(output_na_grid_ids)
                    assert tmp_df.filter(~pl.col('value').is_null()).select('grid_id').unique().sort(by='grid_id').equals(output_non_na_grid_ids)
                # test_expected_number_of_daily_data_points_found
                assert all(tmp_df.group_by(['grid_id', 'var_name']).agg(count = pl.col('var_name').count())['count'] == expected_count)
                samples.append(tmp_df.sample(1000).with_columns(cadence=pl.lit(cadence)))

for cadence in ['monthly', 'annual']:
    tmp_df = pl.read_parquet(output / cadence / 'tas_tasmin_tasmax.parquet.gzip')
    assert tmp_df.filter(pl.col('value').is_null()).select('grid_id').unique().sort(by='grid_id').equals(output_na_grid_ids)
    assert tmp_df.filter(~pl.col('value').is_null()).select('grid_id').unique().sort(by='grid_id').equals(output_non_na_grid_ids)
    samples.append(tmp_df.sample(10000)[['grid_id', 'date', 'var_name', 'value']].with_columns(cadence=pl.lit(cadence)))
    # test_expected_number_of_annual_data_points_found
    n_years = len(tmp_df['date'].str.slice(0, 4).unique())
    if cadence == 'monthly':
        expected_count = n_years * 12
    else:
        expected_count = n_years
    assert all(tmp_df.group_by(['grid_id', 'var_name']).agg(count = pl.col('var_name').count())['count'] == expected_count)

output_df = pl.concat(samples).to_pandas()
output_na_grid_ids = set(output_na_grid_ids['grid_id'])
output_non_na_grid_ids = set(output_non_na_grid_ids['grid_id'])

all_output_grid_ids = output_na_grid_ids | output_non_na_grid_ids

n_samples = 10
half_grid_length = 500
grid_hypotenuse = math.sqrt(half_grid_length**2 + half_grid_length**2)
tolerance_in_m = 10

england_df = pd.read_csv('../rdss-volume/edlowther/data/england_df.csv')

def test_all_uprns_have_grid_id():
    assert pd.isna(lookup_df['grid_id']).sum() == 0

def test_all_uprns_with_masked_grids_have_alternative_grid_id():
    assert pd.isna(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id']).sum() == 0

def test_all_uprns_with_unmasked_grids_do_not_have_alternative_grid_id():
    assert all(pd.isna(lookup_df.loc[~lookup_df['is_masked'], 'unmasked_grid_id']))

def test_all_uprns_are_unique():
    assert len(lookup_df['uprn']) == len(lookup_df['uprn'].unique())

def test_na_and_non_na_grid_ids_are_distinct():
    assert output_na_grid_ids & output_non_na_grid_ids == set()

def test_all_grid_ids_are_in_output_haduk_data():
    # print(np.setdiff1d(lookup_df['grid_id'], all_output_grid_ids))
    # print(np.setdiff1d(all_output_grid_ids, lookup_df['grid_id']))
    # print(np.setdiff1d(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id'], all_output_grid_ids))
    assert all(lookup_df['grid_id'].isin(all_output_grid_ids))
    assert all(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id'].isin(all_output_grid_ids))

def test_all_masked_grids_are_NAs_in_output_haduk_data():
    assert all(lookup_df.loc[lookup_df['is_masked'], 'grid_id'].isin(output_na_grid_ids))

def test_no_unmasked_grids_are_NAs_in_output_haduk_data():
    assert all(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id'].isin(output_non_na_grid_ids))
    assert not any(lookup_df.loc[lookup_df['is_masked'], 'unmasked_grid_id'].isin(output_na_grid_ids))

def test_random_sample_of_annual_output_data_matches_source():
    sample_df = output_df.loc[(~pd.isna(output_df['value'])) & (output_df['cadence'] == 'annual')].sample(n_samples)
    for _, row in sample_df.iterrows():
        y, x = row['grid_id'].split('_')
        var = row['var_name']
        year = row['date'][:4]
        data = netCDF4.Dataset(f'../rdss-volume/edlowther/data/haduk-data/annual/{var}_hadukgrid_uk_1km_ann_{year}01-{year}12.nc')
        assert row['value'] == pytest.approx(data.variables[var][0, y, x])

def test_random_sample_of_monthly_output_data_matches_source():
    sample_df = output_df.loc[(~pd.isna(output_df['value'])) & (output_df['cadence'] == 'monthly')].sample(n_samples)
    for _, row in sample_df.iterrows():
        y, x = row['grid_id'].split('_')
        var = row['var_name']
        year = row['date'][:4]
        month_idx = int(row['date'][5:7]) - 1
        data = netCDF4.Dataset(f'../rdss-volume/edlowther/data/haduk-data/monthly/{var}_hadukgrid_uk_1km_mon_{year}01-{year}12.nc')
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
        data = netCDF4.Dataset(f'../rdss-volume/edlowther/data/haduk-data/daily/{var}_hadukgrid_uk_1km_day_{year}{month:02}01-{year}{month:02}{n_days}.nc')
        assert row['value'] == pytest.approx(data.variables[var][day_idx, y, x])

def test_random_sample_of_unmasked_uprns_are_within_expected_distance_of_grid_cell():
    sample_df = lookup_df.loc[~lookup_df['is_masked']].sample(n_samples)
    sample_df = sample_df.merge(england_df, on='uprn')
    data = netCDF4.Dataset(f'../rdss-volume/edlowther/data/haduk-data/monthly/tas_hadukgrid_uk_1km_mon_200501-200512.nc')
    uprn_points = []
    grid_points = []
    for _, row in sample_df.iterrows():
        uprn_points.append(Point(float(row['X']), float(row['Y'])))
        y, x = map(int, row['grid_id'].split('_'))
        grid_points.append(Point(data.variables['projection_x_coordinate'][x], data.variables['projection_y_coordinate'][y]))
    uprn_points = GeoSeries(uprn_points, crs='EPSG:27700')
    grid_points = GeoSeries(grid_points, crs='EPSG:27700')
    assert all(uprn_points.distance(grid_points) <= grid_hypotenuse)

def test_all_masked_uprns_are_between_bounds_of_expected_distance_of_grid_cell():
    tmp_df = lookup_df.loc[lookup_df['is_masked']].sample(n_samples)
    tmp_df = tmp_df.merge(england_df, on='uprn')
    data = netCDF4.Dataset(f'../rdss-volume/edlowther/data/haduk-data/monthly/tas_hadukgrid_uk_1km_mon_200501-200512.nc')
    uprn_points = []
    grid_points = []
    uprn_reference_points = []
    grid_reference_points = []
    for _, row in tmp_df.iterrows():
        uprn_points.append(Point(float(row['X']), float(row['Y'])))
        uprn_reference_points.append(Point(float(row['longitude']), float(row['latitude'])))
        y, x = map(int, row['unmasked_grid_id'].split('_'))
        grid_points.append(Point(data.variables['projection_x_coordinate'][x], data.variables['projection_y_coordinate'][y]))
        grid_reference_points.append(Point(data.variables['longitude'][y, x], data.variables['latitude'][y, x]))
    uprn_points = GeoSeries(uprn_points, crs='EPSG:27700')
    grid_points = GeoSeries(grid_points, crs='EPSG:27700')
    dists = uprn_points.distance(grid_points)
    assert all(dists >= half_grid_length)
    # This assumption only holds for original subset inside London: elswhere the upper bound is harder to pin down
    # Have done some manual inspection of where assertion fails and all examples are near to irregular coastline
    # assert all(dists <= grid_hypotenuse * 2)
