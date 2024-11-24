# 抓yahoo股票下方的新聞
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# 讀取 CSV 文件並存儲為字典
def read_csv_to_dict(csv_file):
    categories_dict = {}
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                category = row[0]
                numbers = [num.strip() for num in row[1:]]  # 去除多餘空白
                categories_dict[category] = numbers
    except FileNotFoundError:
        print(f"未找到檔案：{csv_file}")
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤：{e}")
    return categories_dict

# 設定輸出字元編碼
sys.stdout.reconfigure(encoding="UTF-8")

# 防止瀏覽器自動關閉
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=option)

url = "https://tw.stock.yahoo.com/"
driver.get(url)
# 讀取 CSV
csv_file = "stock.csv"  # CSV 文件名稱
stock_dict = read_csv_to_dict(csv_file)

count = 0
for category, stock in stock_dict.items():
    count+=1
    print(category,stock)
    # 等待搜索框加載並輸入關鍵字
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ssb-search-input"))
    )
    search_box.send_keys(stock)
    time.sleep(1)
    search_box.send_keys(Keys.ENTER)

    # 等待搜索結果加載
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='StreamMegaItem']"))
    )

    # 找到所有的新聞項目
    news = driver.find_elements(By.CSS_SELECTOR, "li[class*='StreamMegaItem']")
    news = news[:20]

    # 開啟文件寫入結果
    with open("news_articles.txt", "w", encoding="utf-8") as file:
        for count in range(len(news)):
            try:
                # 查找每篇新聞的<a>標籤
                a_tag = news[count].find_element(By.TAG_NAME, "a")
                print("新聞標題：", a_tag.text)
                print("新聞連結：", a_tag.get_attribute("href"))
                file.write(f"新聞標題：{a_tag.text}\n")
                file.write(f"新聞連結：{a_tag.get_attribute('href')}\n")
                file.write("-" * 40 + "\n")

                # 進入新聞詳細頁面
                driver.get(a_tag.get_attribute("href"))

                # 等待新聞內容加載
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='caas-body'] p"))
                )
                
                # 新聞來源
                try:
                    # 找到包含 class="caas-attr-item-author" 的 div
                    author_div = driver.find_element(By.CLASS_NAME, "caas-attr-item-author")
                    # 在 div 中找到 span 標籤
                    span_tag = author_div.find_element(By.TAG_NAME, "span")
                    print("新聞來源：", span_tag.text)
                    file.write(f"新聞來源：{span_tag.text}\n")
                    file.write("-" * 40 + "\n")
                except Exception as e:
                    print(f"未爬取到新聞來源: {e}")
                    
                # 新聞發布時間
                try:
                    # 等待 <div> 出現
                    time_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "caas-attr-time-style"))
                    )
                    # 在 <div> 中找到 <time> 標籤
                    time_tag = time_div.find_element(By.TAG_NAME, "time")
                    print(f"新聞發布時間: {time_tag.text}")
                    file.write(f"新聞發布時間：{time_tag.text}\n")
                    file.write("-" * 40 + "\n")
                except Exception as e:
                    print(f"未爬取到新聞發布時間: {e}")

                # 抓取新聞內容
                print("新聞文章：")
                word = driver.find_elements(By.CSS_SELECTOR, "div[class*='caas-body'] p")
                for p_tag in word:
                    print(p_tag.text)
                    file.write(p_tag.text + "\n")
                file.write("=" * 40 + "\n")

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
    if count == 2:
        break

# 結束並關閉瀏覽器
driver.quit()