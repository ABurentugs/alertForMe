import time
import requests
from bs4 import BeautifulSoup
from plyer import notification

# Settings
URL = "https://www.keishicho-gto.metro.tokyo.lg.jp/keishicho-u/reserve/offerList_detail?tempSeq=363&accessFrom=offerList"  # <-- Replace with your target website
CHECK_INTERVAL = 60  # seconds
TABLE_ID = "target-table-id"  # <-- Set this if the table has an id. Otherwise, we can search by index.
COLUMN_INDEX = 1  # <-- 0-based index: first column is 0, second is 1, etc.

def get_target_column(url, table_id=None, column_index=0):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table
    if table_id:
        table = soup.find("table", id=table_id)
    else:
        table = soup.find("table")  # first table found

    if table is None:
        raise ValueError("No table found on the page.")

    # Extract all rows
    rows = table.find_all("tr")

    # Extract the target column data
    column_data = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) > column_index:
            column_data.append(cells[column_index].get_text(strip=True))
    
    return column_data

def notify_user(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5
    )

def main():
    print(f"Monitoring {URL} - Column {COLUMN_INDEX} of table {TABLE_ID or '(first table)'}...")
    previous_column_data = get_target_column(URL, TABLE_ID, COLUMN_INDEX)

    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            current_column_data = get_target_column(URL, TABLE_ID, COLUMN_INDEX)
            if current_column_data != previous_column_data:
                print("Update detected in the target column!")
                notify_user("Column Update Detected", f"Changes detected at {URL}")
                previous_column_data = current_column_data
            else:
                print("No changes detected.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
