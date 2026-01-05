import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By

# 1. 初始化資料庫 
def init_db():
    conn = sqlite3.connect('quotes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            tags TEXT
        )
    ''')
    conn.commit()
    return conn

# 2. 設定 Chrome 
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') 

# 啟動 Chrome 
browser = webdriver.Chrome(options=chrome_options)

try:
    conn = init_db()
    # 存取網站
    browser.get('http://quotes.toscrape.com/js/')
    
    # 爬取前 5 頁
    for page in range(5):
        print(f"正在爬取第 {page + 1} 頁...")
        # 等待 js 渲染內容
        time.sleep(2)  
        
        # 抓取該頁面所有的名言區塊
        quotes_elements = browser.find_elements(By.CLASS_NAME, 'quote')
        
        for element in quotes_elements:
            text = element.find_element(By.CLASS_NAME, 'text').text
            author = element.find_element(By.CLASS_NAME, 'author').text
            # 將標籤清單合併為逗號分隔的字串
            tags_list = [t.text for t in element.find_elements(By.CLASS_NAME, 'tag')]
            tags_str = ",".join(tags_list)
            
            # 寫入資料庫
            conn.execute(
                "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
                (text, author, tags_str)
            )
        
        conn.commit()
        
        # 模擬點擊「Next」換頁
        if page < 4:
            try:
                next_btn = browser.find_element(By.PARTIAL_LINK_TEXT, "Next")
                next_btn.click()
            except:
                print("找不到下一頁按鈕。")
                break
                
    print("爬取完成！資料已成功存入 quotes.db")

finally:
    # 關閉瀏覽器
    browser.quit()
    if 'conn' in locals():
        conn.close()