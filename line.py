import requests
from dotenv import load_dotenv
import os

load_dotenv()

#アクセストークンとユーザーIDを環境変数(.env)から取得
ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
KOSEI_ID = os.getenv("KOSEI_ID")

def send_line_kosei(text):
    # APIエンドポイント
    url = "https://api.line.me/v2/bot/message/push"
    # ヘッダー情報
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    # 送るメッセージ
    message = {
        "to": KOSEI_ID,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    # POSTリクエスト送信
    response = requests.post(url, headers=headers, json=message)

    # 結果の表示
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

if __name__=="__main__":
    send_line_kosei("テスト送信です")
