from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os, json
from functions import weather as wt
from dotenv import load_dotenv

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
                        # json_data = json.loads(body)
                        # user_id = json_data["events"][0]["source"]["userId"]
                        msg = event.message.text
                        ai_msg = msg[:5].lower() #這行開始為chatGPT
                        reply_msg =""
                        if ai_msg == "go ai":
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
                            reply_msg = wt.weather_search()

                        else:
                            reply_msg = "尚不支援本功能，請重新輸入"

                        message = TextSendMessage(text=reply_msg)
                        line_bot_api.reply_message(event.reply_token,message)

                    except:
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

        return HttpResponse()

    else:
        return HttpResponseBadRequest()
