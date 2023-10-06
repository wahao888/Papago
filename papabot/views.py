from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os, json
from functions import mydb
from dotenv import load_dotenv

from django.contrib.auth.models import User
from papabot.models import LineId
from django.contrib.auth import authenticate

# 加載.env文件
load_dotenv()
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.environ.get("LINE_CHANNEL_SECRET"))

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    try:
                        json_data = json.loads(body)
                        userId = json_data["events"][0]["source"]["userId"]
                        msg = event.message.text
                        ai_msg = msg[:5].lower() #這行開始為chatGPT
                        reply_msg =""
                        if ai_msg == "go ai":
                            if mydb.verify(userId):
                                reply_msg = "請先進行帳號連結，再使用此功能。"
                            else:
                                openai.api_key = os.environ.get("YOUR_API_KEY_NAME")
                                response = openai.Completion.create(
                                    model = "text-davinci-003",
                                    prompt = msg[5:],
                                    max_tokens = 512,
                                    temperature = 0.5,
                                )
                                reply_msg = response["choices"][0]["text"].replace("\n","")
                            # line_bot_api.push_message(user_id, TextMessage(text=msg))

                        elif msg == "天氣預報":
                            account = mydb.readDB(userId)
                            if account == "請先進行帳號連結":
                                reply_msg = account
                            else:
                                reply_msg = mydb.readWeather(account)

                        elif msg == "行事曆":
                            account = mydb.readDB(userId)
                            if account == "請先進行帳號連結":
                                reply_msg = account
                            else:
                                reply_msg = mydb.readTrip(account)

                        elif msg == "帳號連結":
                            if mydb.verify(userId):
                                global temp
                                temp = userId
                                reply_msg = "請點擊以下網址進行帳號驗證：\nhttps://papago-abc54f89f470.herokuapp.com/papabot/check/"
                            else:
                                reply_msg = "帳號已連結"

                        else:
                            reply_msg = "尚不支援本功能，請重新輸入"

                        message = TextSendMessage(text=reply_msg)
                        line_bot_api.reply_message(event.reply_token,message)

                    except:
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

        return HttpResponse()

    else:
        return HttpResponseBadRequest()


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get("account")
        password = request.POST.get("pwd")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            userLine = LineId (
                line_id = temp,
                user_id = user.id
            )
            userLine.save()
            res = "<h1>驗證並連結成功</h1>"
            return HttpResponse(res)
        else:
            res = "<h1>帳號或密碼錯誤</h1>"
            return HttpResponse(res)

    return render(request, 'check.html', {})