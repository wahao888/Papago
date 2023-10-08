#papago/map/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import requests
import os
from dotenv import load_dotenv
import re
import json
from .models import TripInfo, WholeTripInfo, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

load_dotenv()
GOOGLE_MAP_API_KEY = os.environ.get('GOOGLE_MAP_API_KEY')
if GOOGLE_MAP_API_KEY is None:
    raise EnvironmentError("GOOGLE_MAP_API_KEY is not set.")
google_maps_endpoint = 'https://maps.googleapis.com/maps/api/geocode/json'

openai.api_key = os.environ.get("YOUR_API_KEY_NAME")
if openai.api_key is None:
    raise EnvironmentError("OPENAI_API_KEY is not set.")

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
if openweather_api_key is None:
    raise EnvironmentError("OPENWEATHER_API_KEY is not set.")


@login_required
def index(request):
    return render(request, 'map.html')


#產生景點
@login_required
@csrf_exempt
def generate_itinerary(request):
    if request.method == "POST":
        location = request.POST.get('location')
        days = request.POST.get('days')
        
        #使用openai生成景點
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=f"請條列出到{location} {days}天的景點",
            max_tokens=150,
            temperature=0.6
        )
        print(response.choices[0].text)
        places = response.choices[0].text.split("\n")
        places = [re.sub(r'^\d+\.\s*|\*|：.*$|^.*、|-(.*)$', '', place.strip()) for place in places if place.strip()]
        

        #找出景點的經緯度
        result = []
        for place in places:
            lat, lng = get_coordinates_from_address(place)
            result.append({"name": place, "lat": lat, "lng": lng})
        # print(result)

        return JsonResponse({"places": result})
    else:
        return render(request, 'map.html')
    

#取得經緯度
def get_coordinates_from_address(address):
    params = {
        'address': address,
        'key': GOOGLE_MAP_API_KEY
    }
    
    response = requests.get(google_maps_endpoint, params=params)
    
    if response.status_code == 200:
        json_response = response.json()
        if json_response['status'] == 'OK':
            location = json_response['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None

#還沒使用
def your_view_function(request):
    context = {
        'GOOGLE_MAP_API_KEY': os.environ.get('GOOGLE_MAP_API_KEY'),
    }
    return render(request, 'map.html', context)


#取得城市天氣資訊
@csrf_exempt
def get_weather_forecast(request):
    if request.method == "POST":
        location = request.POST.get('location')
        print("location:",location)
        #找出城市的經緯度
        city_lat, city_lng = get_coordinates_from_address(location)

        #使用openweather取得天氣資訊
        api_key = openweather_api_key
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={city_lat}&lon={city_lng}&units=metric&lang=zh_tw&appid={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json() 

            forecast_data = []
            for i in range(0, 40, 8):
                day_data = weather_data['list'][i]
                temperature = day_data['main']['temp']
                weather_main = day_data['weather'][0]['main']
                weather_icon = day_data['weather'][0]['icon']
                
                forecast_data.append({
                    'temperature': temperature,
                    'weather_main': weather_main,
                    'weather_icon': weather_icon
                })
            print("Forecast data:", forecast_data)
            return JsonResponse({"forecast_data": forecast_data})
            
            #原本只取溫度
            # temperature = weather_data.get('list')[0].get('main').get('temp') 
            # print("temperature:",temperature)
            # return JsonResponse({"temperature": temperature})
        else:
            return JsonResponse({"error": "Unable to get weather data"}, status=response.status_code)
    else:
        return render(request, 'map.html')
    

# 儲存行程
@login_required
@require_POST
@csrf_exempt
def save_trip(request):
    if request.method == 'POST':
        user = request.user
        WholeTripInfo.objects.filter(user=user).delete()  # 刪除舊的行程信息

        # 生成 JSON 對象
        trip_data = {
            "trip_name": request.POST.get('trip_name'),
            "trip_day": int(request.POST.get('trip_day')),
            "day_tags": json.loads(request.POST.get('day_tags', '[]')),
            "location_tags": json.loads(request.POST.get('location_tags', '[]')),
            "location_info_map": json.loads(request.POST.get('location_info_map', '[]')),
        }

        print("trip_data:", trip_data)

        # 保存到數據庫
        WholeTripInfo.objects.create(
            user=user,
            trip_data=trip_data
        )

        return JsonResponse({'status': 'success', 'message': 'Trip saved successfully'})

    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid method'})

#取得儲存的行程
@login_required
@csrf_exempt
def get_saved_trip(request):
    user = request.user
    saved_trips = WholeTripInfo.objects.filter(user=user).values()
    print("User ID:", user)
    print("Saved trips:", saved_trips)
    return JsonResponse({'status': 'success', 'data': list(saved_trips)})
