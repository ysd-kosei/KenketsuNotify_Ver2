from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from line import send_line_kosei
import os

# ユーザー情報（ここに実際の情報を入力してください）
KENKETSUSHA_CODE = "3698193495"
PASSWORD = "Donate20"

#保存ファイル名
LAST_VALUE_FILE = "last_value.txt"


def read_last_value():
    if not os.path.exists(LAST_VALUE_FILE):
        return None
    with open(LAST_VALUE_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def write_last_value(value):
    with open(LAST_VALUE_FILE, "w", encoding="utf-8") as f:
        f.write(value)


# Chrome起動オプション（ヘッドレスにも対応可能）
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 必要ならヘッドレスモードを有効化
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.kenketsu.jp/")

    # フォームが読み込まれるのを待つ
    wait = WebDriverWait(driver, 10)
    code_input = wait.until(EC.presence_of_element_located((By.NAME, "Login:j_id78:j_id80")))
    pass_input = wait.until(EC.presence_of_element_located((By.NAME, "Login:j_id78:j_id82")))

    # ログイン情報の入力
    code_input.send_keys(KENKETSUSHA_CODE)
    pass_input.send_keys(PASSWORD)

    # ログインボタン（onclickでJSが動く形式）を実行
    login_script = """jsfcljs(document.getElementById('Login:j_id78'),'Login:j_id78:j_id87,Login:j_id78:j_id87','');"""
    driver.execute_script(login_script)

    # ログイン後のページ遷移待ち
    time.sleep(3)  # 必要に応じてWebDriverWaitに変更可能

    # ログイン後のURL確認
    current_url = driver.current_url
    print(f"ログイン成功: 現在のURL = {current_url}")
    
    # ログイン後のHTMLを取得
    html_source = driver.page_source

    soup = BeautifulSoup(html_source, "html.parser")
    article = soup.find("article", class_="mod-top-user-date")
    
    if article is None:
    raise Exception("予約情報が取得できませんでした。ページ構造が変わっている可能性があります。")

    dt_elements = article.find_all("dt")
    dd_elements = article.find_all("dd")

    data = {}

    for dt, dd in zip(dt_elements, dd_elements):
        key = dt.get_text(strip=True)
        value = dd.get_text(strip=True)

        if key =="日時":
            data["datetime"] = value
        elif key=="献血種類":
            data["type"] =value
        elif key=="場所":
            data["place"] = value

    print(data)
    
    # メッセージ形式に整形
    message = f"予約情報:\n{data['datetime']}\n{data['type']}\n{data['place']}"
    
    last_message = read_last_value()


    if message != last_message:
        diff_message = f"[変更がありました]\n\n--- 前回 ---\n{last_message or '（なし）'}\n\n--- 今回 ---\n{message}"
        send_line_kosei(diff_message)
        write_last_value(message)
        print("差分あり → 通知＆last_value更新")
    else:
       send_line_kosei("[変更はありませんでした]")
       print("差分なし → 通知のみ")

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    driver.quit()
