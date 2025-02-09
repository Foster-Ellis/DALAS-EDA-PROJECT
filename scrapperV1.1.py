import requests
from bs4 import BeautifulSoup
url = "https://en.wikipedia.org/wiki/List_of_inventors"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

content = soup.find("div", class_="mw-content-ltr")

inventors_list = []

uls = content.find_all("ul") if content else []

for ul in uls:
    for li in ul.find_all("li"):
        #Full text
        full_text = li.get_text()
        
        #Get the name
        a_tag = li.find("a")
        if a_tag:
            inventor_name = a_tag.text
            #Extract the invention
            invention = full_text.replace(inventor_name, "").strip(" ,.–")
            inventors_list.append((inventor_name, invention))

#skip all the insignificant data
for inventor, invention in inventors_list[28:1101]:
    print(f"{inventor}: {invention}")
