from django.shortcuts import render

# Create your views here.
from .forms import TravelLogForm
from .models import TravelLog
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator  # 分頁功能

from blog.forms import ProfileForm
from blog.models import Profile
from blog.forms import TravelLogForm
from blog.models import TravelLog


import requests

# Create your views here.


@login_required
def SaveProfile(request):  # 進入網址/blog/profile
    saved = False
    user = request.user
    if request.method == "POST":
        # Get the posted form
        dict1 = {}
        for i in request.FILES.getlist('picture'):  # request資料取的檔案的list
            dict1['picture'] = i  # 將list復原成請求單個檔案的格式
            MyProfileForm = ProfileForm(request.POST, dict1)

            if MyProfileForm.is_valid():  # 檢查請求是否通過
                profile = Profile()
                profile.name = MyProfileForm.cleaned_data["name"]
                profile.picture = MyProfileForm.cleaned_data["picture"]
                profile.user = user
                profile.save()  # 儲存檔案
                saved = True
            else:
                MyProfileForm = ProfileForm()

    # 跳到save.html確定是否存成功
    return render(request, 'saved.html', {"saved": saved})


@login_required
def show(request):      # 進入網址/blog/show
    user = request.user
    photos = Profile.objects.filter(user=user)   # 查詢當前已登錄用戶上傳的圖片
    folders = photos.values('folder').distinct()    # 查詢不同的文件夾路徑
    selected_folder = request.GET.get('folder')      # 選擇文件夾，過濾圖片
    if selected_folder:
        photos = photos.filter(folder=selected_folder)

    # 分頁（使用Django內置的分頁功能）
    paginator = Paginator(photos, 10)  # 每頁顯示10張圖片
    page = request.GET.get('page')
    photos = paginator.get_page(page)

    # 在show.html顯示圖片
    return render(request, 'show.html', {'folders': folders, 'selected_folder': selected_folder, 'photos': photos})


@login_required
def create_travel_log(request):
    if request.method == 'POST':
        form = TravelLogForm(request.POST)
        if form.is_valid():
            travel_log = form.save(commit=False)  # 存取內容
            travel_log.user = request.user  # 存該用戶資訊
            travel_log.save()
            return redirect('travel_logs')
    else:
        form = TravelLogForm()

    return render(request, 'create_travel_log.html', {'form': form})


@login_required
def view_travel_logs(request):
    travel_logs = TravelLog.objects.filter(
        user=request.user).order_by('-date_created')  # 確認為該用戶
    selected_log = None

    if request.method == 'GET':
        log_id = request.GET.get('log_id')
        if log_id:
            selected_log = get_object_or_404(
                TravelLog, id=log_id, user=request.user)

    return render(request, 'view_travel_logs.html', {'travel_logs': travel_logs, 'selected_log': selected_log})
