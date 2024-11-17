import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sys

# 設定輸出字元編碼
sys.stdout.reconfigure(encoding="UTF-8")

# 防止瀏覽器自動關閉
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=option)

url = "https://tw.news.yahoo.com/"
driver.get(url)

# 尋找定位框
search_box = driver.find_element(By.ID, "ybar-sbq")
search_box.send_keys("台積電股價")
time.sleep(1)
search_box.send_keys(Keys.ENTER)

# 讓爬蟲有足夠的時間爬取
time.sleep(3)

try:
    # 定位包含新聞的父 <li> 元素 (根據 Yahoo 的 HTML 結構調整選擇器)
    news = driver.find_elements(By.CSS_SELECTOR, "li[class*='StreamMegaItem']")
    
    with open("news_articles.txt", "w", encoding="utf-8") as file:  # 開啟文件
        # 遍歷每個 <li>，找到內部的 <a>
        for li in news:
            try:
                # 查找 <li> 中的 <a>
                a_tag = li.find_element(By.TAG_NAME, "a")
                print("新聞標題：", a_tag.text)
                print("新聞連結：", a_tag.get_attribute("href"))
                # 寫入新聞標題和連結到文件
                file.write(f"新聞標題：{a_tag.text}\n")
                file.write(f"新聞連結：{a_tag.get_attribute('href')}\n")
                file.write("-" * 40 + "\n")
                
                # 點擊進入新聞
                a_tag.click()
                time.sleep(3)  # 等待新頁面加載
                
                # 抓取新聞內容
                try:
                    word = driver.find_elements(By.CSS_SELECTOR, "div[class*='caas-body'] p")
                    for p_tag in word:
                        # 打印新聞內容
                        print("新聞文章：", p_tag.text)
                        # 寫入新聞內容到文件
                        file.write(p_tag.text + "\n")
                    file.write("=" * 40 + "\n")
                except Exception as e:
                    print("無法找到新聞內容：", e)
                
                # 返回搜尋結果頁面
                driver.back()
                time.sleep(2)
            
            except Exception as e:
                print("此 <li> 中未找到 <a>：", e)

except Exception as e:
    print("執行時發生錯誤：", e)

finally:
    driver.quit()
