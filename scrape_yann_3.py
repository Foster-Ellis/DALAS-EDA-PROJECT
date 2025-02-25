import requests
import csv
from lxml import html
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to request page: {e}")
        return None

# Parse the page HTML and return all timeline block nodes.
def parse_timeline_blocks(page_html):
   
    try:
        tree = html.fromstring(page_html)
        # Use XPath to locate the main container by id
        container_xpath = '//div[@id="wphtsp-history-design-1"]'
        container = tree.xpath(container_xpath)
        if not container:
            logging.error("Could not find the timeline container node. Please check the XPath!")
            return []

        # Find all .wphtsp-timeline-block elements under the container
        blocks = container[0].xpath('.//div[contains(@class, "wphtsp-timeline-block")]')
        if not blocks:
            logging.warning("No timeline blocks found!")
        return blocks
    except Exception as e:
        logging.error(f"Failed to parse HTML: {e}")
        return []

# Parse a single timeline block and extract Year, Name, and Content.
# The title is expected in the format "1543: On the Revolutions of Celestial Spheres",
# using a colon to separate the year (as string) and the name.
# Temporarily store the entire 'year_part' as a string in CSV, no integer conversion.

def parse_block(block):

    try:
        # Get the title <a> element
        title_elem = block.xpath('.//h2[@class="wphtsp-content-title"]/a')
        if not title_elem:
            logging.warning("Title <a> element not found, skipping this block.")
            return None
        title_text = title_elem[0].text_content().strip()

        if ':' not in title_text:
            logging.warning(f"Title format is not as expected: {title_text}")
            return None

        # Split by colon, store everything before the colon as year_part (string)
        year_part, name_part = [part.strip() for part in title_text.split(":", 1)]

        # Get the content
        content_elem = block.xpath('.//div[contains(@class, "wphtsp-content-inner")]')
        content_text = content_elem[0].text_content().strip() if content_elem else ""

        return {
            'year': year_part,
            'name': name_part,
            'content': content_text
        }
    except Exception as e:
        logging.error(f"Exception occurred while parsing a timeline block: {e}")
        return None

# Main crawler function: fetch the page, parse each timeline block, and return the results.
def crawl_science_timeline(url):
    
    page_html = fetch_page(url)
    if not page_html:
        return []

    blocks = parse_timeline_blocks(page_html)
    if not blocks:
        logging.error("No timeline blocks found. Crawler will stop.")
        return []

    # Parse each block using a functional approach
    parsed_data = list(filter(None, map(parse_block, blocks)))
    return parsed_data

def write_to_csv(data, filename='raw_data_3.csv'):
    """Write the extracted data to a CSV file."""
    if not data:
        logging.warning("No data to write to the CSV file.")
        return

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['year', 'name', 'content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        logging.info(f"Data successfully written to CSV file: {filename}")
    except Exception as e:
        logging.error(f"Failed to write to CSV file: {e}")

if __name__ == '__main__':
    target_url = "https://www.missingtheforest.com/history-of-science-timeline/"
    data = crawl_science_timeline(target_url)
    if data:
        write_to_csv(data)
    else:
        logging.error("No valid data was retrieved by the crawler.")
