from django.contrib.auth.models import User
from map.models import TripInfo
from papabot.models import LineId
from functions import weather


def readDB(line_Id):
    user = User.objects.filter(username=line_Id)
    lineId = LineId.objects.filter(line_id=line_Id)
    if not user and not lineId:
        return "請先進行帳號連結"
    elif not user:
        msg = lineId[0].user_id
    else:
        msg = user[0].id
    return msg

def readWeather(userid):
    tripinfo = TripInfo.objects.filter(user=userid)
    city = tripinfo[0].trip_name[:3]
    if "台" in city:
        city = city.replace("台","臺")

    msg = weather.weather_search(city)

    return msg

def readTrip(userid):
    tripinfo = TripInfo.objects.filter(user=userid)
    tripName = tripinfo[0].trip_name
    locationName = f"{tripName}\n"

    for i in range(len(tripinfo)):
        locationName += tripinfo[i].location_name + "\t"

    return locationName