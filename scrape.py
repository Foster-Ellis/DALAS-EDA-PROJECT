import requests
from bs4 import BeautifulSoup
import csv
from lxml import html

# ---------------------------------
# 1. Global Config & Utility Functions
# ---------------------------------

def fetch_page(url, timeout=10):
    """
    Fetch a webpage with basic error handling.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/113.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"ERROR: Failed to request page: {e}")
        return None

# -----------------------------------------------------------------------------
# 2. Crawler 1: Parse a specific table and save to CSV
# -----------------------------------------------------------------------------

def parse_table_from_site1(html_content):
    """
    Parse a specific <table> structure and return data as a list of [year, discovery_name, inventor].
    """
    soup = BeautifulSoup(html_content, 'html.parser')
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
        # Remove duplicate inventor string from discovery name
        name = name_text.replace(inventor, "").replace("/", "").strip()
        data.append([year, name, inventor])
    return data

def save_to_csv_site1(data, filename):
    """
    Write Site1 data to CSV.
    Columns: ["Year of Invention", "Name of Inventor", "Name of Scientific Discovery"]
    """
    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year of Invention", "Name of Inventor", "Name of Scientific Discovery"])
        writer.writerows(data)

def crawl_site1():
    """
    Fetch page, parse table, and save CSV for Site1.
    """
    url = "https://press.uchicago.edu/Misc/Chicago/284158.html"
    html_content = fetch_page(url)
    if html_content:
        table_data = parse_table_from_site1(html_content)
        save_to_csv_site1(table_data, "raw_data_1.csv")
        print("Site1 data extraction completed, saved to raw_data_1.csv")
    else:
        print("ERROR: Failed to retrieve HTML content for Site1.")

# -----------------------------------------------------------------------------
# 3. Crawler 2: Parse timeline blocks and save to CSV
# -----------------------------------------------------------------------------

def parse_timeline_blocks_from_site2(page_html):
    """
    Find the container with id="wphtsp-history-design-1" and parse timeline blocks.
    """
    try:
        tree = html.fromstring(page_html)
        container_xpath = '//div[@id="wphtsp-history-design-1"]'
        container = tree.xpath(container_xpath)
        if not container:
            print("ERROR: Timeline container not found for Site2. Check the XPath!")
            return []
        blocks = container[0].xpath('.//div[contains(@class, "wphtsp-timeline-block")]')
        if not blocks:
            print("WARNING: No timeline blocks found for Site2!")
        return blocks
    except Exception as e:
        print(f"ERROR: Failed to parse HTML for Site2: {e}")
        return []

def parse_block_site2(block):
    """
    Parse a timeline block: title in the format "year: name" and content.
    """
    try:
        title_elem = block.xpath('.//h2[@class="wphtsp-content-title"]/a')
        if not title_elem:
            print("WARNING: Title <a> element not found in a block, skipping for Site2.")
            return None

        title_text = title_elem[0].text_content().strip()
        if ':' not in title_text:
            print(f"WARNING: Title format unexpected: {title_text}")
            return None

        year_part, name_part = [part.strip() for part in title_text.split(":", 1)]

        content_elem = block.xpath('.//div[contains(@class, "wphtsp-content-inner")]')
        content_text = content_elem[0].text_content().strip() if content_elem else ""

        return {
            'year': year_part,
            'name': name_part,
            'content': content_text
        }
    except Exception as e:
        print(f"ERROR: Error parsing a timeline block for Site2: {e}")
        return None

def crawl_site2():
    """
    Fetch page, parse timeline blocks, and write CSV for Site2.
    """
    url = "https://www.missingtheforest.com/history-of-science-timeline/"
    page_html = fetch_page(url)
    if not page_html:
        print("ERROR: Failed to retrieve HTML content for Site2.")
        return

    blocks = parse_timeline_blocks_from_site2(page_html)
    if not blocks:
        print("ERROR: No timeline blocks found for Site2. Crawler will stop.")
        return

    parsed_data = list(filter(None, map(parse_block_site2, blocks)))
    write_to_csv_site2(parsed_data, "raw_data_2.csv")

def write_to_csv_site2(data, filename='raw_data_2.csv'):
    """
    Write Site2 results to CSV with fields ['year', 'name', 'content'].
    """
    if not data:
        print("WARNING: No data to write to CSV for Site2.")
        return

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['year', 'name', 'content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        print(f"Data successfully written to {filename} for Site2.")
    except Exception as e:
        print(f"ERROR: Failed to write CSV for Site2: {e}")

# -----------------------------------------------------------------------------
# 4. Crawler 3: Parse <li> elements and save to CSV
# -----------------------------------------------------------------------------

def parse_li_elements_from_site3(page_html):
    """
    Parse specific <li> elements using XPath.
    """
    try:
        tree = html.fromstring(page_html)
        li_xpath = '//*[@id="mw-content-text"]/div[1]/ul/li'
        li_elements = tree.xpath(li_xpath)
        if not li_elements:
            print("WARNING: No <li> elements found on Site3. Check the XPath or page structure.")
        return li_elements
    except Exception as e:
        print(f"ERROR: Failed to parse HTML for Site3: {e}")
        return []

def parse_item_site3(li_element):
    """
    Extract year from <b> tag and full text from an <li>.
    Append link info at the end.
    """
    try:
        year_elem = li_element.xpath('.//b/text()')
        if not year_elem:
            return None
        year_text = year_elem[0].strip()

        raw_text = li_element.xpath('string(.)').strip()

        a_elements = li_element.xpath('.//a')
        link_parts = []
        for a in a_elements:
            a_title = a.get('title') or ''
            a_text = a.text_content().strip()
            if a_title or a_text:
                link_parts.append(f"{a_title}({a_text})")

        combined_content = raw_text + "\nLinks: " + " | ".join(link_parts)

        return {
            'year': year_text,
            'content': combined_content
        }
    except Exception as e:
        print(f"ERROR: Error parsing an item for Site3: {e}")
        return None

def crawl_site3():
    """
    Fetch page, parse <li> elements, and write CSV for Site3.
    """
    url = "https://en.wikipedia.org/wiki/Timeline_of_historic_inventions"
    page_html = fetch_page(url)
    if not page_html:
        print("ERROR: Failed to retrieve HTML content for Site3.")
        return

    li_elements = parse_li_elements_from_site3(page_html)
    if not li_elements:
        print("ERROR: No <li> elements found. Aborting crawl for Site3.")
        return

    parsed_data = list(filter(None, map(parse_item_site3, li_elements)))
    write_to_csv_site3(parsed_data, "raw_data_3.csv")

def write_to_csv_site3(data, filename='raw_data_3.csv'):
    """
    Write Site3 results to CSV with fields ['year', 'content'].
    """
    if not data:
        print("WARNING: No data to write to CSV for Site3.")
        return

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['year', 'content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        print(f"Data successfully written to {filename} for Site3.")
    except Exception as e:
        print(f"ERROR: Failed to write CSV for Site3: {e}")

# -----------------------------------------------------------------------------
# 5. Main Entry Point (Call crawlers as needed)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Starting crawl for Site1...")
    crawl_site1()

    print("Starting crawl for Site2...")
    crawl_site2()

    print("Starting crawl for Site3...")
    crawl_site3()

    print("All crawls completed.")
