import rasterio as rio


def obtainvalue(lat, lon, pollutant):
    """
        Takes a lat and lon and returns a value for the relevant pollutant from raster

        Args
            lat (float): Latitude
            lon (float): Longitude
            pollutant (str): Pollutant type - NO2, PM2.5 or PM10

        Returns
            value (float): Value of pollution in μg/m3
    """

    if pollutant == 'NO2':
        raster = 'data/NO2_2025.tif'
    elif pollutant == 'PM2.5':
        raster = 'data/PM2_5_2025.tif'
    elif pollutant == 'PM10':
        raster = 'data/PM10_2025.tif'
    else:
        raster = 'data/NO2_2025.tif'

    with rio.open(raster) as src:
        lonlat = (lon, lat)
        sample = list(src.sample([lonlat]))
        value = sample[0][0]

    return value
