let map;
let marker;
let markers = [];
let currentPosition;
let selectedMarker;
let directionsService;
let directionsRenderer;
let infodetail; //autocomplete的詳細資料
let infowindow; //自動產生行程的詳細資料
let markerId = 0;
let markerInfoMap = new Map();  // 用於存儲標記和 InfoWindow 的對應關係
let detailInfoMap = new Map();  // 用於存儲標記和 infodetail 的對應關係
let today = new Date(); // 獲取今天的日期
let locationInfoMap = new Map(); //保存地點資訊給路徑使用(0915)也給存資料庫用(0922)
let markerNumber = 1; // 標記編號
let trip_day = 1; // 行程天數
let driveTimeBetweenLocations = []; // 用於儲存行駛時間的陣列
let trip_name;
let location_name;

// 初始化地圖
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 23.477709920659528, lng: 120.95694302203336 }, // 玉山
        zoom: 9
    });


    // 從 localStorage 讀取 location-list
    const locationList = JSON.parse(localStorage.getItem("location-list")) || [];
    // 更新頁面
    locationList.forEach((location) => {
        document.getElementById("location-list").innerHTML += `
            <li class="list-group-item">
                ${location.name}
                <button class="btn-close float-end remove"></button>
            </li>
        `;
    });

    // 從 localStorage 中恢復 locationInfoMap
    const storedLocationInfoArray = JSON.parse(localStorage.getItem('locationInfo')) || [];
    locationInfoMap = new Map(storedLocationInfoArray);
    
    // 使用恢復的 locationInfoMap 重新創建地圖上的標記和 InfoWindow
    locationInfoMap.forEach((locationInfo, name) => {
        // 創建標記
        const marker = new google.maps.Marker({
            position: locationInfo.location,
            map: map,
            title: locationInfo.name
        });
    }); 

    // 當用戶登入後調用這個函數
    //rebuildLocationInfoMap(); 

    //搜尋框及自動完成
    navigator.geolocation.getCurrentPosition(function(position) {
        currentPosition = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };
        map.setCenter(currentPosition);
        map.setZoom(13);

    
        // 定義台灣的地理邊界
        const taiwanBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(21.8, 120),  // 西南角
        new google.maps.LatLng(25.3, 122)   // 東北角
        );
        //設定搜尋框
        const autocomplete = new google.maps.places.Autocomplete(
            document.getElementById("search"),{
                types: [
                    "restaurant","airport","zoo","tourist_attraction","museum"
                ],
                bounds: taiwanBounds,
                strictBounds: true 
        });

        //設定自動完成，當按下地點時，取得地點資訊
        autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            
            selectedMarker = {
                location: place.geometry.location,
                placeId: place.place_id,
                name: place.name,
                address: place.formatted_address,
                phoneNumber: place.formatted_phone_number,
                rating: place.rating,
                reviews: place.reviews,
                opening_hours: place.opening_hours ? place.opening_hours : "none",
                photos: place.photos ?  place.photos : "none",
            };
            //console.log("location:", selectedMarker.location);
            //console.log("location_type:", typeof selectedMarker.location);

            //地圖中心移動到選擇的地點
            map.setCenter(selectedMarker.location);


            marker = new google.maps.Marker({
                map: map
            });

            marker.setPosition(selectedMarker.location);//建立標記

            const formattedOpeningHours = selectedMarker.opening_hours.weekday_text ? selectedMarker.opening_hours.weekday_text.join('<br>') : "none";
            const photoUrl = (selectedMarker.photos && selectedMarker.photos[0]) 
                ? selectedMarker.photos[0].getUrl()
                : "無照片可用";

            //顯示詳細資訊
            infodetail = new google.maps.InfoWindow();
            infodetail.setContent(`
                <h3>${selectedMarker.name}</h3>
                <div>地址: ${selectedMarker.address}</div>
                <div>電話: ${selectedMarker.phoneNumber}</div>
                <div>評分: ${selectedMarker.rating}</div>
                <div>營業時間: ${
                    selectedMarker.opening_hours === "none" ? "無資料" : formattedOpeningHours
                }</div>
                <img src="${photoUrl}" alt="未提供照片" style="width: 200px;"/>
                `);

                //將該地點的名稱和相應的infodetail添加到detailInfoMap
                detailInfoMap.set(selectedMarker.name, {
                    infodetail: infodetail,
                    marker: marker
                });

                //將selectedMarker內容加到locationInfoMap，給路徑使用(0915)
                locationInfoMap.set(selectedMarker.name, selectedMarker);
            infodetail.open(map, marker);
        });
    });//搜尋框及自動完成結束

    //後端利用openai自動產生行程，前端按"產生行程"按鈕後，後端回傳行程地名與座標
    document.getElementById("generate").addEventListener("click", function(event) {
        event.preventDefault();
            
        //前端取得行程地名與座標
        const location = $("#location").val();
        const days = $("#days").val();
        trip_name = location + days + "天行程";
        location_name = location;
        trip_day = days;



        //傳資料到後端，並加入氣溫資訊
        $.post("/map/get_weather_forecast/", {location: location}, function(response) {
            const forecast_data = response.forecast_data;
            //console.log("forecast_data:", forecast_data);
            let forecastHtml = '';

            forecast_data.forEach(function(dayData) {
                const temperature = dayData.temperature;
                const weatherMain = dayData.weather_main;
                const weatherIcon = dayData.weather_icon;
                const iconUrl = `http://openweathermap.org/img/wn/${weatherIcon}.png`;
                // 格式化日期
                const options = { year: 'numeric', month: 'long', day: 'numeric' };
                const formattedDate = today.toLocaleDateString('zh-TW', options);

                
                forecastHtml += `
                    <div class="card mb-2 p-2" style="background-color: #F2EDE4; color: #A89F91;">
                        <h5 class="card-title">${formattedDate}</h5>
                        <p class="card-text">氣溫：${temperature}°C</p>
                        <p class="card-text">天氣型態：${weatherMain}<img src="${iconUrl}" alt="${weatherMain}"/></p>
                        
                    </div>
                `;
                // 更新日期到下一天
                today.setDate(today.getDate() + 1);
            });
        
            document.getElementById("weather").innerHTML = forecastHtml;
            });
        
        //傳資料到後端
        $.post('/map/generate_itinerary/', { location: location, days: days }, function(data) {
            //console.log("Received data from backend:", data);
            //console.log("lat:", data.places[0].lat);
            //console.log("lng:", data.places[0].lng);
            
            //for each前端取得詳細資訊加到selectedMarker
            const geocoder = new google.maps.Geocoder();
            const service = new google.maps.places.PlacesService(map);
            data.places.forEach((place, index) => {
                if (place.lat && place.lng) {
                const latLng = new google.maps.LatLng(place.lat, place.lng);
                //console.log("index:", index);
                //console.log("latLng:", latLng);
                //console.log("type_lat:",typeof place.lat, "type_lng:",typeof place.lng);
                //console.log("lat:", latLng.lat(), "lng:", latLng.lng());
                
                // 使用 Geocoder 進行逆地理編碼
                geocoder.geocode({'location': latLng}, function(results, status) {
                    if (status === google.maps.GeocoderStatus.OK) {
                        if (results[0]) {
                            const placeId = results[0].place_id;
                            //console.log("Place ID: ", placeId);

                            // 使用獲得的 placeId 來獲取詳細資訊
                            service.getDetails({
                                placeId: placeId,
                                fields: ['name', 'formatted_address', 'formatted_phone_number', 'rating', 'reviews', 'opening_hours','photos']
                            }, function(details, status) {
                                //console.log("Status:", status);
                                //console.log("Details:", details);
                                if (status === google.maps.places.PlacesServiceStatus.OK) {
                                    //console.log("status_placesService:", status);
                                    if (details) {
                                        // 儲存詳細資訊
                                            
                                            const generateDetails = {
                                                location: latLng,
                                                placeId: details.place_id ?? "未提供",
                                                name: place.name,
                                                address: details.formatted_address ?? "未提供",
                                                phoneNumber: details.formatted_phone_number ?? "未提供",
                                                rating: details.rating ?? "未提供",
                                                reviews: details.reviews ?? [],
                                                opening_hours: details.opening_hours ?? "未提供",
                                                photos: details.photos  ?  details.photos  : "none",
                                            };
                                            //console.log("generateDetails:", generateDetails);
                                            //console.log("location:", generateDetails.location);
                                            //console.log("details.photos:", details.photos);
                                        
                                        // 在地圖上創建標記
                                        const generateMarker = new google.maps.Marker({
                                            position: generateDetails.location,
                                            map: map,
                                            title: generateDetails.name
                                        });
                                        

                                        //顯示詳細資訊
                                        infowindow = new google.maps.InfoWindow();
                                        const formattedGenerateDetailsOpeningHours = generateDetails.opening_hours && generateDetails.opening_hours.weekday_text 
                                            ? generateDetails.opening_hours.weekday_text.join('<br>') 
                                            : "none";
                                        const generateDetailsphotoUrl = (generateDetails.photos && generateDetails.photos[0] && typeof generateDetails.photos[0].getUrl === 'function') 
                                        ? generateDetails.photos[0].getUrl() 
                                        : "null";

                                        infowindow.setContent(`
                                            <h3>${generateDetails.name}</h3>
                                            <div>地址: ${generateDetails.address}</div>
                                            <div>電話: ${generateDetails.phoneNumber}</div>
                                            <div>評分: ${generateDetails.rating}</div>
                                            <div>營業時間: ${
                                                formattedGenerateDetailsOpeningHours === "none" 
                                                ? "未提供"
                                                : formattedGenerateDetailsOpeningHours
                                            }</div>
                                            <img src="${generateDetailsphotoUrl}" alt="未提供照片" style="width: 200px;"/>
                                        `);
                                        infowindow.open(map, generateMarker);

                                        // 保存 marker 和 InfoWindow(0914)
                                        markerInfoMap.set(generateDetails.name, {
                                            marker: generateMarker,
                                            infoWindow: infowindow
                                        });
                                        
                                        //加入行程標籤在視窗左側行程規劃底下
                                        document.getElementById("location-list").innerHTML += `
                                            <li class="list-group-item">
                                                ${generateDetails.name}
                                                <button class="btn-close float-end remove"></button>
                                            </li>
                                        `;
                                        
                                        // 將新地點添加到 localStorage 中的地點列表
                                        const detailList = JSON.parse(localStorage.getItem("location-list")) || [];
                                        detailList.push(generateDetails);
                                        localStorage.setItem("location-list", JSON.stringify(detailList));
                                        
                                        //將該地點的名稱和相應的infowindow添加到markerInfoMap給路徑使用(0915)
                                        locationInfoMap.set(generateDetails.name, generateDetails);

                                        drawPathsBetweenLocations(); // 繪製路徑(0915)
                                        

                                        // 將locationInfoMap轉換為陣列，儲存到 localStorage，以便在頁面重新加載時使用
                                        const locationInfoArray = Array.from(locationInfoMap.entries());
                                        localStorage.setItem('locationInfo', JSON.stringify(locationInfoArray));
                                        }
                                    } else {
                                        console.log("Missing details");
                                }
                            });
                        }
                    }
                    else {
                        console.log("Geocoder failed due to: " + status);
                    }
                });
            }
            });
        });
    });//自動產生行程結束
}
//initmap結束


// 加入行程標籤(在initMap外面)
document.getElementById("add").addEventListener("click", function() {
    document.getElementById("location-list").innerHTML += `
        <li class="list-group-item">
            ${selectedMarker.name}
            <button class="btn-close float-end remove"></button>
        </li>
    `
    const locationList = JSON.parse(localStorage.getItem("location-list")) || [];
    locationList.push(selectedMarker);
    localStorage.setItem("location-list", JSON.stringify(locationList));

    drawPathsBetweenLocations(); // 繪製路徑(0915)

    // 將locationInfoMap轉換為陣列，儲存到 localStorage，以便在頁面重新加載時使用
    const locationInfoArray = Array.from(locationInfoMap.entries());
    localStorage.setItem('locationInfo', JSON.stringify(locationInfoArray));
});

// 刪除行程標籤
document.getElementById("location-list").addEventListener("click", function(e) {
    if (e.target.classList.contains("remove")) {
        e.target.parentElement.remove();
        const locationName = e.target.parentNode.innerText.trim();

        // 刪除地圖上的相應標記(0914)
        const markerInfo = markerInfoMap.get(locationName);
        const detailInfo = detailInfoMap.get(locationName);
        if (markerInfo) {
            markerInfo.marker.setMap(null);
            markerInfoMap.delete(locationName);
        }

        if (detailInfo) {
            detailInfo.marker.setMap(null);
            detailInfoMap.delete(locationName);
        } 

        // 刪除 locationInfoMap 的相應項目
        if (locationInfoMap.has(locationName)) {
            locationInfoMap.delete(locationName);
        }
        
        const locationList = JSON.parse(localStorage.getItem("location-list")) || [];
        const newLocationList = locationList.filter(function(location) {
            if (location.name === locationName) return false;
            return true;
        });
        localStorage.setItem("location-list", JSON.stringify(newLocationList));

        drawPathsBetweenLocations(); // 繪製路徑(0915)

        // 將locationInfoMap轉換為陣列，儲存到 localStorage，以便在頁面重新加載時使用
        const locationInfoArray = Array.from(locationInfoMap.entries());
        localStorage.setItem('locationInfo', JSON.stringify(locationInfoArray));
    }
});

// 點擊 location-list 中的項目顯示infoWindow, infodetail
document.getElementById("location-list").addEventListener("click", function(e) {
    if (e.target.tagName === "LI") {
        const locationName = e.target.innerText.trim();
        const markerInfo = markerInfoMap.get(locationName);
        const detailInfo = detailInfoMap.get(locationName);
        if (markerInfo) {
            markerInfo.infoWindow.open(map, markerInfo.marker);
        }
        if (detailInfo) {
            detailInfo.infodetail.open(map, detailInfo.marker);
        }
    }
});

// 清空行程
document.getElementById("clearItinerary").addEventListener("click", function() {
    // 清空 localStorage 中的 location-list
    localStorage.removeItem("location-list");

    // 清空頁面上的行程列表
    document.getElementById("location-list").innerHTML = '';

    // 清空地圖上的所有標記
    deleteMarkers();

    // 清空路徑
    if (directionsRenderer) {
        directionsRenderer.setMap(null);
    }

    // 清空 locationInfoMap
    locationInfoMap.clear();

    //清空localStorage
    localStorage.clear();
});

    

// 在地圖上添加標記
function addMarker(location) {
    let marker = new google.maps.Marker({
        position: location,
        map: map,
        draggable:false,
        customId: markerId++
    });
    markers.push(marker);  // 將新標記添加到標記數組中
}


// 刪除所有標記
function deleteMarkers() {
    // 遍歷 markerInfoMap 來移除每個標記
    markerInfoMap.forEach(function(value, key) {
        value.marker.setMap(null);
    });

    // 遍歷 detailInfoMap 來移除每個標記
    detailInfoMap.forEach(function(value, key) {
        value.marker.setMap(null);
    });

    // 清空 markerInfoMap 和 detailInfoMap
    markerInfoMap.clear();
    detailInfoMap.clear();
    locationInfoMap.clear();
}

// 繪製路徑(0915)
function drawPathsBetweenLocations() {
    const locationList = [];

    // 從 DOM 的 li 元素填充 locationList
    document.querySelectorAll("#location-list li").forEach((li) => {
        const locationName = li.textContent.trim();
        const details = locationInfoMap.get(locationName);
        if (details) {
            locationList.push(details);
        }
    });

    if (locationList.length > 1) {
        // 初始化 directionsService 和 directionsRenderer
        if (!directionsService) {
            directionsService = new google.maps.DirectionsService();
        }
        if (!directionsRenderer) {
            directionsRenderer = new google.maps.DirectionsRenderer({
                map,
            });
        }

        const origin = locationList[0].location;
        const destination = locationList[locationList.length - 1].location;
        const waypoints = locationList.slice(1, -1).map((locationInfo) => {
            return {
                location: new google.maps.LatLng(locationInfo.location.lat(), locationInfo.location.lng()),
                stopover: true
            };
        });

        directionsService.route(
            {
                origin: new google.maps.LatLng(origin.lat(), origin.lng()),
                destination: new google.maps.LatLng(destination.lat(), destination.lng()),
                waypoints: waypoints,
                optimizeWaypoints: false,
                travelMode: 'DRIVING'
            },
            function(response, status) {
                if (status === "OK") {
                    directionsRenderer.setDirections(response);
                    updateLocationListWithTime(response);//更新行駛時間(0918)
                }
            }
        );
    } else {
        if (directionsRenderer) {
            directionsRenderer.setMap(null);
        }
    }
}//繪製路徑結束

// 更新行駛時間(0918)
function updateLocationListWithTime(response) {
const locationListElement = document.getElementById("location-list");

// 刪除所有現有的時間標籤
const existingTimeTags = locationListElement.querySelectorAll(".time-tag");
existingTimeTags.forEach(timeTag => timeTag.remove());

// 獲取現有的地點元素
const existingLocations = locationListElement.querySelectorAll("li"); 

// 遍歷各段路徑（legs）來獲取行駛時間
const legs = response.routes[0].legs;

// 清空陣列
driveTimeBetweenLocations = [];

for (let i = 0; i < legs.length; i++) {
    const leg = legs[i];

    // 創建時間標籤
    const timeTag = document.createElement("span");
    timeTag.className = "time-tag";
    timeTag.textContent = "車程: " + leg.duration.text;

    // 在現有地點後面插入時間標籤
    if (existingLocations[i]) {
        locationListElement.insertBefore(timeTag, existingLocations[i].nextSibling);
    }

    // 將行駛時間加入陣列
    driveTimeBetweenLocations.push(leg.duration.text);
}
}


//產生天數標籤(0919)
function generateDayTags(days) {
    const locationListElement = document.getElementById("location-list");
    const colors = ["#6A8CAF", "#A89AC9", "#89A88F", "#D4A073", "#D4AEB2"];  // 顏色列表

    for (let i = 1; i <= days; i++) {
        const dayTag = document.createElement("li");
        dayTag.className = "day-tag";
        dayTag.textContent = "第" + i + "天";
        dayTag.style.backgroundColor = colors[(i - 1) % colors.length];
        dayTag.draggable = true;
        locationListElement.appendChild(dayTag);
    }
}

// 在用戶點擊 "保存行程" 按鈕時觸發 AJAX 請求(0922)
$("#saveTripButton").click(function() {
// 先獲取所有的地點
var locationTags = [];
$("#location-list li").each(function() {
    locationTags.push($(this).text());
});

// 把 locationInfoMap 轉換成一個數組來儲存
const latLngInfoMap = new Map();
// 從 locationInfoMap 中提取經緯度並存儲到 latLngInfoMap
locationInfoMap.forEach((value, key) => {
    const lat = value.location.lat(); 
    const lng = value.location.lng(); 
    latLngInfoMap.set(key, { lat, lng });
});
// 將 latLngInfoMap 轉換為陣列
const latLngInfoArray = Array.from(latLngInfoMap.entries());
console.log("latLngInfoArray:", latLngInfoArray);

$.ajax({
    url: '/map/save_trip/',  
    method: 'POST',
    data: {
        'trip_name': trip_name,
        'location_name': location_name,
        'trip_day': trip_day,
        'location_tags': JSON.stringify(locationTags),
        'location_info_map': JSON.stringify(latLngInfoArray),

    },
    success: function(response) {
        // 行程成功保存後的操作
        console.log("行程成功保存:", response);
    },
    error: function(error) {
        // 如果保存行程出錯，這裡會捕獲錯誤
        console.log("保存行程出錯:", error);
    }
});
});

//重建資料庫中的 locationInfoMap(0926)
// 在用戶登入後呼叫這個函數
function loadSavedTrip() {
$.ajax({
    url: '/map/get_saved_trip/',  
    method: 'GET',
    data: {
        'user_id': loggedInUserId  // 用戶的 ID
    },
    success: function(response) {
        if (response.status === 'success') {
            const savedTrips = response.data;
            const latLngInfoMap = new Map();
            savedTrips.forEach(trip => {
                latLngInfoMap.set(trip.location_name, {
                    lat: trip.latitude,
                    lng: trip.longitude
                });
            });
            // 現在你有了重建好的 latLngInfoMap，你可以使用這個 Map 來重建行程
        } else {
            console.log("無法獲取保存的行程:", response.message);
        }
    },
    error: function(error) {
        console.log("獲取保存的行程出錯:", error);
    }
});
}



$(function() {
    $("#location-list").sortable({
        cursor: "move",  // 當拖動時，游標會變成四個方向的箭頭
        update: function(event, ui) {
            // 當排序完成並且 DOM 更新後，重新繪製路徑
            drawPathsBetweenLocations(); // 繪製路徑(0915)
        }
    });
    $("#location-list").disableSelection();
});

