from django.contrib.auth.models import User
from map.models import WholeTripInfo
from papabot.models import LineId
from functions import weather


def verify(line_Id): #驗證lineid是否存在資料庫
    user = User.objects.filter(username=line_Id)
    lineId = LineId.objects.filter(line_id=line_Id)
    if not user and not lineId:
        return True
    return False


def readDB(line_Id): #驗證lineid，如果有，回傳userid
    user = User.objects.filter(username=line_Id)
    lineId = LineId.objects.filter(line_id=line_Id)
    if not user and not lineId:
        return "請先進行帳號連結"
    elif not user:
        msg = lineId[0].user_id
    else:
        msg = user[0].id
    return msg

def readWeather(userid): #用linebot讀取資料庫行程名稱，再進行天氣預報爬蟲
    wholeTripinfo = WholeTripInfo.objects.filter(user=userid)
    if not wholeTripinfo:
        return "目前無設定好的行程，請先安排行程"
    else:
        userTripinfo = wholeTripinfo[0].trip_data
        city = userTripinfo["trip_name"][:3]
        if "台" in city:
            city = city.replace("台","臺")

        msg = weather.weather_search(city)

        return msg

def readTrip(userid):  #用linebot讀取資料庫行程
    wholeTripinfo = WholeTripInfo.objects.filter(user=userid)
    if not wholeTripinfo:
        return "目前無設定好的行程，請先安排行程"
    else:
        userTripinfo = wholeTripinfo[0].trip_data
        tripName = userTripinfo["trip_name"]
        days = userTripinfo["day_tags"]
        locations = userTripinfo["location_tags"]
        tripDays = userTripinfo["trip_day"]
        orders = len(days) + len(locations)
        msg = f"{tripName}\n"
        start = 0
        for td in range(tripDays):
            if td == tripDays - 1:
                end = start + (orders - days[td]["order"])
            else:
                end = start + (days[td + 1]["order"] - days[td]["order"]) - 1
            msg += "<" + days[td]["text"] + ">" + "\n"
            for loc in range(start, end):
                msg += locations[loc]["text"] + "\n"
            msg += "\n"

            if td == tripDays - 1:
                break
            else:
                start = end

        return msg.strip()