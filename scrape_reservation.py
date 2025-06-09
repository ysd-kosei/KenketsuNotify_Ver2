from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from line import send_line_kosei

# ユーザー情報（ここに実際の情報を入力してください）
KENKETSUSHA_CODE = "3698193495"
PASSWORD = "Donate20"

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

    # LINE送信
    send_line_kosei(message)

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    driver.quit()
