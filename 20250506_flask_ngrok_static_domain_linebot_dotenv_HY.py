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

# 載入 .env 檔案
load_dotenv()

# 從環境變數取得 Token 和 Secret
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

app = Flask(__name__)

# 替换为你自己的 Channel Access Token 和 Channel Secret
configuration = Configuration(access_token=LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 处理根路径 "/" (用於檢測flask server是否有順利運作)
@app.route("/")
def index():
    return "Hello, Flask is running!"

# 处理LINE Bot 的 Webhook 回调路由
@app.route("/callback", methods=['POST'])
def callback():
    # 获取 X-Line-Signature 头部信息
    signature = request.headers['X-Line-Signature']

    # 获取请求体数据
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 验证签名并处理 Webhook 请求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 定义消息处理函数
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 使用 ApiClient 建立与 LINE Messaging API 的连接
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)# 创建 MessagingApi 实例
        # 创建 ReplyMessageRequest，用于发送回复消息
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,          # 使用事件的回复令牌
            messages=[TextMessage(text=event.message.text)]  # 将接收到的消息文本作为回复
        )
        
        # 使用 MessagingApi 的 reply_message_with_http_info 方法发送消息
        line_bot_api.reply_message_with_http_info(reply_message_request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) #host='0,0,0,0',允許ngrok無受限IP的訪問; port=5000, 須與ngork的port=5000一樣
