from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_MAP_API_KEY = os.environ.get('GOOGLE_MAP_API_KEY')
if GOOGLE_MAP_API_KEY is None:
    raise EnvironmentError("GOOGLE_MAP_API_KEY is not set.")
openai.api_key = os.environ.get("YOUR_API_KEY_NAME")
if openai.api_key is None:
    raise EnvironmentError("OPENAI_API_KEY is not set.")
google_maps_endpoint = 'https://maps.googleapis.com/maps/api/geocode/json'

@csrf_exempt
def generate_itinerary(request):
    if request.method == "POST":
        location = request.POST.get('location')
        days = request.POST.get('days')
        
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=f"請條列出到{location} {days}天的景點",
            max_tokens=150,
            temperature=0.6
        )

        print(response.choices[0].text)
        places = response.choices[0].text.split("\n")
        places = [place.strip() for place in places if place.strip()]

        result = []
        for place in places:
            lat, lng = get_coordinates_from_address(place)
            result.append({"name": place, "lat": lat, "lng": lng})

        print(result)
        return JsonResponse({"places": result})
    else:
        return render(request, 'index.html')

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

if __name__ == '__main__':
    address_input = "1600 Amphitheatre Parkway, Mountain View, CA"  # 這是 Google 總部的地址
    latitude, longitude = get_coordinates_from_address(address_input)

    if latitude and longitude:
        print(f'地址：{address_input}')
        print(f'緯度：{latitude}, 經度：{longitude}')
    else:
        print('無法獲取經緯度資訊。')


def your_view_function(request):
    context = {
        'GOOGLE_MAP_API_KEY': os.environ.get('GOOGLE_MAP_API_KEY'),
    }
    return render(request, 'index.html', context)

# Modifications made by ChatGPT

# Simulate sending data to front-end (Replace with real logic)
def send_data_to_frontend(request):
    sample_data = [
        {'name': '1. 龍山寺', 'lat': 25.0373106, 'lng': 121.4998654},
        {'name': '2. 松山文創園區', 'lat': 25.0438366, 'lng': 121.5606383},
        {'name': '3. 台北 101', 'lat': 25.0329636, 'lng': 121.5654268},
        # ... (Add more places)
    ]
    return JsonResponse({"places": sample_data})
