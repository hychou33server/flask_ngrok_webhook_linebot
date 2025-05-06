import os
from dotenv import load_dotenv  # 引入 dotenv
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# load .env file
load_dotenv()

# 從.env file取得 Token 和 Secret
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

app = Flask(__name__)

# Channel Access Token 和 Channel Secret
configuration = Configuration(access_token=LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 處理根路徑 "/" (用於檢測flask server是否有順利運作)
@app.route("/")
def index():
    return "Hello, Flask is running!"

# 處理LINE Bot的Webhook回调路由
@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature headers信息
    signature = request.headers['X-Line-Signature']

    # 取得request body數據
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證簽名並處理 Webhook 請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 輸入訊息處理function
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 使用 ApiClient 建立與 LINE Messaging API 的連接
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)# 創建 MessagingApi 實例
        # 創建 ReplyMessageRequest，用於發送回覆訊息
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,          # 使用事件的回覆令牌
            messages=[TextMessage(text=event.message.text)]  # 將接收到的輸入訊息文本作為回覆訊息
        )
        
        # 使用 MessagingApi 的 reply_message_with_http_info 方法發送訊息
        line_bot_api.reply_message_with_http_info(reply_message_request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) #host='0,0,0,0',允許ngrok無受限IP的訪問; port=5000, 須與ngrok的port=5000一樣
