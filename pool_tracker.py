import time
import re
import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

URL = "https://www.stadt-zuerich.ch/de/stadtleben/sport-und-erholung/sport-und-badeanlagen/hallenbaeder/city.html"
CSV_FILE = "pool_visitors.csv"

def get_visitor_count():
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Edge(options=edge_options)
    try:
        driver.get(URL)
        for _ in range(15):
            time.sleep(1)
            body_text = driver.find_element(By.TAG_NAME, "body").text
            match = re.search(r"Anzahl Gäste[\s:]*(\d+)", body_text)
            if match:
                return int(match.group(1))
        return None
    except Exception as e:
        print(f"Error reading page: {e}")
        return None
    finally:
        driver.quit()

def save_reading(dt, count):
    file_exists = os.path.isfile(CSV_FILE)
    
    # Pre-calculate time buckets for flexible future visualizations
    slot_5m  = f"{dt.strftime('%H')}:{(dt.minute // 5) * 5:02d}"
    slot_15m = f"{dt.strftime('%H')}:{(dt.minute // 15) * 15:02d}"
    slot_30m = f"{dt.strftime('%H')}:{(dt.minute // 30) * 30:02d}"
    
    row = [
        dt.strftime("%Y-%m-%d %H:%M:%S"), # Exact Timestamp (down to the second)
        dt.strftime("%Y-%m-%d"),          # Date (YYYY-MM-DD)
        dt.strftime("%A"),                # Day_of_Week (Monday, Tuesday...)
        dt.weekday(),                     # Day_Num (0=Mon, 6=Sun)
        dt.strftime("%H:%M"),             # Exact Time (HH:MM)
        dt.hour,                          # Hour (0-23)
        dt.minute,                        # Exact Minute (0-59)
        slot_5m,                          # 5-min bucket (e.g., 07:05)
        slot_15m,                         # 15-min bucket (e.g., 07:15)
        slot_30m,                         # 30-min bucket (e.g., 07:30)
        count if count is not None else ""
    ]
    
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Date", "Day_of_Week", "Day_Num", 
                "Time", "Hour", "Minute", "Slot_5m", "Slot_15m", "Slot_30m", "Visitors"
            ])
        writer.writerow(row)

def main():
    now = datetime.now(ZoneInfo("Europe/Zurich"))
    
    # Only record during Hallenbad City opening hours (06:00 to 22:00)
    if 6 <= now.hour < 22:
        count = get_visitor_count()
        save_reading(now, count)
        print(f"[{now.strftime('%H:%M:%S')}] Recorded: {count}")
    else:
        print(f"[{now.strftime('%H:%M:%S')}] Pool closed. Skipping.")

if __name__ == "__main__":
    main()
