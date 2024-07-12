import geopandas as gpd

# Download source data from: 
# https://geoportal.statistics.gov.uk/datasets/eb2332f49e554b2980ac9003b1c9711e/explore
# and unzip into `shp` directory
regions_shp = gpd.read_file('./shp/RGN_DEC_2021_EN_BFE.shp')
london_shp = regions_shp.loc[regions_shp['RGN21NM'] == 'London']
london_shp.to_file('./shp/london.shp')
