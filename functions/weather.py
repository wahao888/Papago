from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from urllib.request import quote
from datetime import datetime
import requests
# Create your views here.


def hello(request):
    text = """<h1>welcome to alvin!!!</h1>"""
    return HttpResponse(text)
    return render(request, "hello.html", {})


def weather_search():
    city = '新北市'
    location = quote(city, encoding="utf-8")
    msg = "找不到天氣資訊"
    try:
        api_key = 'CWB-8338FA8C-D3FC-4BA9-859F-E576EF7D4BC5'

        url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={api_key}&format=JSON&locationName={location}'

        res = requests.get(url)

        data = res.json()
        # datas = []
        location = data["records"]["location"][0]["locationName"]
        weather_elements = data["records"]["location"][0]["weatherElement"]
        msg = f"［{city}天氣預報］\n"
        for i in range(3):
            # info = []
            st = datetime.strptime(
                weather_elements[0]["time"][i]["startTime"], r"%Y-%m-%d %H:%M:%S")
            start_time = st.strftime(r"%d號 %H點")
            et = datetime.strptime(
                weather_elements[0]["time"][i]["endTime"], r"%Y-%m-%d %H:%M:%S")
            end_time = et.strftime(r"%d號 %H點")
            weather_state = weather_elements[0]["time"][i]["parameter"]["parameterName"]
            rain_prob = weather_elements[1]["time"][i]["parameter"]["parameterName"]
            min_tem = weather_elements[2]["time"][i]["parameter"]["parameterName"]
            comfort = weather_elements[3]["time"][i]["parameter"]["parameterName"]
            max_tem = weather_elements[4]["time"][i]["parameter"]["parameterName"]
            # data = [start_time, end_time, max_tem,
            #         min_tem, rain_prob, weather_state, comfort]
            msg += f"{start_time}至{end_time}\n天氣為{weather_state}，{comfort}，最高溫{max_tem}度，最低溫{min_tem}度，降雨機率{rain_prob}%\n\n"
            # datas.append(data)
            # print(datas)
            # print(location)
            # print(start_time)
            # print(end_time)
            # print(weather_state)
            # print(rain_prob)
            # print(min_tem)
            # print(max_tem)
            # print(comfort)
            # print('-'*20)
        # return render(request, "weather.html", {"city": city, "datas": datas})
        return msg
    except:
        return msg
