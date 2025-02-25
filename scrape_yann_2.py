import requests
import csv
from lxml import html
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch the HTML content from the given URL.
def fetch_page(url, timeout=10):
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to request page: {e}")
        return None
# Parse the HTML and find all <li> elements under the specified container.
def parse_li_elements(page_html):
    
    try:
        tree = html.fromstring(page_html)
        li_xpath = '//*[@id="mw-content-text"]/div[1]/ul/li'
        li_elements = tree.xpath(li_xpath)
        if not li_elements:
            logging.warning("No <li> elements found. Check the XPath or the page structure.")
        return li_elements
    except Exception as e:
        logging.error(f"Failed to parse HTML: {e}")
        return []


# Extract the year from the <b> tag and build a combined content string.
# If there's no <b> text, return None (skip silently).
def parse_item(li_element):

    try:
        # Year: get text from <b>
        year_elem = li_element.xpath('.//b/text()')
        if not year_elem:
            # Skip silently if <b> is not found
            return None
        year_text = year_elem[0].strip()

        # Get all text from the li
        raw_text = li_element.xpath('string(.)').strip()

        # Build link expansions: 'title(text)'
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
        logging.error(f"Exception occurred while parsing an item: {e}")
        return None

# Main crawler function that fetches the page, locates li elements, and parses them.
def crawl_wiki_timeline(url):
    
    page_html = fetch_page(url)
    if not page_html:
        return []

    li_elements = parse_li_elements(page_html)
    if not li_elements:
        logging.error("No <li> elements found. Aborting the crawl.")
        return []

    parsed_data = list(filter(None, map(parse_item, li_elements)))
    return parsed_data

# Write the extracted data to a CSV file.
def write_to_csv(data, filename='raw_data_2.csv'):    
    if not data:
        logging.warning("No data to write to CSV.")
        return

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['year', 'content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        logging.info(f"Data successfully written to {filename}")
    except Exception as e:
        logging.error(f"Failed to write CSV file: {e}")

if __name__ == '__main__':
    target_url = "https://en.wikipedia.org/wiki/Timeline_of_historic_inventions"
    results = crawl_wiki_timeline(target_url)
    if results:
        write_to_csv(results)
    else:
        logging.error("No valid data retrieved by the crawler.")
