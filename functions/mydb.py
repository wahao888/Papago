from django.contrib.auth.models import User
from map.models import TripInfo
from functions import weather


def readDB(line_id):
    user = User.objects.get(username=line_id)
    res = ""
    res += str(user.id)
    return res

def readWeather():
    tripinfo = TripInfo.objects.filter(user=1)
    city = tripinfo[0].trip_name[:3]
    if "台" in city:
        city = city.replace("台","臺")

    msg = weather.weather_search(city)

    return msg

def readTrip():
    tripinfo = TripInfo.objects.filter(user=1)
    tripName = tripinfo[0].trip_name
    locationName = f"{tripName}\n"

    for i in range(len(tripinfo)):
        locationName += tripinfo[i].location_name + "\t"

    return locationName