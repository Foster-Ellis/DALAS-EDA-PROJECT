import requests
from bs4 import BeautifulSoup
url = "https://en.wikipedia.org/wiki/List_of_inventors"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

content = soup.find("div", class_="mw-content-ltr")

inventors_list_general = []

uls = content.find_all("ul") if content else []

for ul in uls:
    for li in ul.find_all("li"):
        #Full text
        full_text = li.get_text()
        inventors_list_general.append(full_text)

url = "https://en.wikipedia.org/wiki/Timeline_of_scientific_discoveries"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

content = soup.find("div", class_="mw-content-ltr")

inventors_list = []

uls = content.find_all("ul") if content else []

for ul in uls:
    for li in ul.find_all("li"):
        #Full text
        full_text = li.get_text()
        inventors_list.append((full_text))


del inventors_list_general[0:28]
del inventors_list_general[1073:]
del inventors_list[341:]
