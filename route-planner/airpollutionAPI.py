import requests


class PointQuality:
    """
    Class representing air quality at specific locations

    Attributes
        lat (float): Latitude
        lon (float): Longitude
        apikey (str): Valid OpenWeather API key

    Methods
        .__init___(): Constructs the object

    """
    def __init__(self, lat, lon, apikey):
        """
        Constructs all the necessary attributes for the locations object.

        Args
            lat (float): Latitude
            lon (float): Longitude
            apikey (str): Valid OpenWeather API key

        Returns
            None
        """
        self.lat = str(lat)
        self.lon = str(lon)
        self.apikey = apikey

    def pollutionvalues(self, pollutant):
        """
        Constructs all the necessary attributes for the locations object.

        Args
            pollutant (str): Pollutant for which value is required (co, no, no2, o3, so2, pm2_5, pm10, nh3)

        Returns
            pollutantvalue (float): Value of pollution in μg/m3
        """
        response = requests.get(
                "http://api.openweathermap.org/data/2.5/air_pollution?lat=" +
                self.lat + "&lon=" + self.lon + "&appid=" + self.apikey)
        airq = response.json()
        components = airq['list'][0]['components']
        pollutantvalue = (components[pollutant])
        return pollutantvalue


point1 = PointQuality(52.679935, -1.921781, "82f376a18ef0356724cdaeed7d4d390e")



