import requests
apikey = "82f376a18ef0356724cdaeed7d4d390e"
lat = "52.679935"
lon = "-1.921781"
response = requests.get("http://api.openweathermap.org/data/2.5/air_pollution?lat="+lat+"&lon="+lon+"&appid="+apikey)
print(response.status_code)
