import requests
from bs4 import BeautifulSoup
import csv

def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def parse_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("table", {
        "width": "450",
        "cellpadding": "5",
        "cellspacing": "0",
        "align": "left"
    })
    if not table:
        return []

    rows = table.find_all("tr", valign="top")
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        year = cols[0].get_text(strip=True)
        second_cell = cols[1]
        inventor_tag = second_cell.find("b")
        if inventor_tag:
            inventor = inventor_tag.get_text(strip=True).replace("/", "").strip()
        else:
            inventor = "Unknown"
        name_text = second_cell.get_text(strip=True)
        name = name_text.replace(inventor, "").replace("/", "").strip()
        data.append([year, name, inventor])
    return data

def save_to_csv(data, filename):
    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Name", "Inventor"])
        writer.writerows(data)

def main():
    url = "https://press.uchicago.edu/Misc/Chicago/284158.html"
    html = fetch_html(url)
    if html:
        table_data = parse_table(html)
        save_to_csv(table_data, "raw_data_1.csv")
    else:
        print("Failed to retrieve HTML content.")

if __name__ == "__main__":
    main()
