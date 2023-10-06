import requests
from urllib.request import quote
from datetime import datetime


def weather_search(city):
    location = quote(city, encoding="utf-8")
    msg = "找不到天氣資訊"
    try:
        api_key = 'CWB-8338FA8C-D3FC-4BA9-859F-E576EF7D4BC5'

        url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={api_key}&format=JSON&locationName={location}'

        res = requests.get(url)

        data = res.json()
        location = data["records"]["location"][0]["locationName"]
        weather_elements = data["records"]["location"][0]["weatherElement"]
        msg = f"【{city}天氣預報】\n"
        for i in range(3):
            st = datetime.strptime(
                weather_elements[0]["time"][i]["startTime"], r"%Y-%m-%d %H:%M:%S")
            start_time = st.strftime(r"%m/%d %H:00")
            et = datetime.strptime(
                weather_elements[0]["time"][i]["endTime"], r"%Y-%m-%d %H:%M:%S")
            end_time = et.strftime(r"%m/%d %H:00")
            weather_state = weather_elements[0]["time"][i]["parameter"]["parameterName"]
            rain_prob = weather_elements[1]["time"][i]["parameter"]["parameterName"]
            min_tem = weather_elements[2]["time"][i]["parameter"]["parameterName"]
            comfort = weather_elements[3]["time"][i]["parameter"]["parameterName"]
            max_tem = weather_elements[4]["time"][i]["parameter"]["parameterName"]

            msg += f"{start_time} - {end_time}\n天氣為{weather_state}，{comfort}，最高溫{max_tem}度，最低溫{min_tem}度，降雨機率{rain_prob}%\n\n"

        return msg.strip()
    except:
        return msg
