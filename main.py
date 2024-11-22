import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# 設定輸出字元編碼
sys.stdout.reconfigure(encoding="UTF-8")

# 初始化資料庫
conn = sqlite3.connect("news_articles.db")
cursor = conn.cursor()

# 建立表格
cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    source TEXT,
    publish_time TEXT,
    content TEXT
)
""")
conn.commit()

# 防止瀏覽器自動關閉
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=option)

url = "https://tw.news.yahoo.com/"
driver.get(url)

# 等待搜索框加載並輸入關鍵字
search_box = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ybar-sbq"))
)
search_box.send_keys("台積電股價")
time.sleep(1)
search_box.send_keys(Keys.ENTER)

# 等待搜索結果加載
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='StreamMegaItem']"))
)

# 找到所有的新聞項目
news = driver.find_elements(By.CSS_SELECTOR, "li[class*='StreamMegaItem']")
news = news[:20]

for count in range(len(news)):
    try:
        # 查找每篇新聞的<a>標籤
        a_tag = news[count].find_element(By.TAG_NAME, "a")
        title = a_tag.text
        link = a_tag.get_attribute("href")
        print("新聞標題：", title)
        print("新聞連結：", link)

        # 進入新聞詳細頁面
        driver.get(link)

        # 等待新聞內容加載
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='caas-body'] p"))
        )
        
        # 新聞來源
        source = None
        try:
            author_div = driver.find_element(By.CLASS_NAME, "caas-attr-item-author")
            span_tag = author_div.find_element(By.TAG_NAME, "span")
            source = span_tag.text
            print("新聞來源：", source)
        except Exception as e:
            print(f"未爬取到新聞來源: {e}")
            
        # 新聞發布時間
        publish_time = None
        try:
            time_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "caas-attr-time-style"))
            )
            time_tag = time_div.find_element(By.TAG_NAME, "time")
            publish_time = time_tag.text
            print(f"新聞發布時間: {publish_time}")
        except Exception as e:
            print(f"未爬取到新聞發布時間: {e}")

        # 抓取新聞內容
        content = []
        word = driver.find_elements(By.CSS_SELECTOR, "div[class*='caas-body'] p")
        for p_tag in word:
            content.append(p_tag.text)
        content = "\n".join(content)
        print("新聞文章：", content)

        # 插入資料庫
        cursor.execute("""
            INSERT INTO news (title, link, source, publish_time, content)
            VALUES (?, ?, ?, ?, ?)
        """, (title, link, source, publish_time, content))
        conn.commit()

        # 點擊返回上一頁
        driver.back()

        # 等待返回後頁面加載完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='StreamMegaItem']"))
        )
        
        # 再次查找所有新聞項目
        news = driver.find_elements(By.CSS_SELECTOR, "li[class*='StreamMegaItem']")
        news = news[:20]
    except Exception as e:
        print("處理過程中發生錯誤：", e)

# 結束並關閉瀏覽器
driver.quit()
conn.close()
