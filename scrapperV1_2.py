import requests
from bs4 import BeautifulSoup
import csv

url = "https://en.wikipedia.org/wiki/List_of_inventors"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

content = soup.find("div", class_="mw-content-ltr")

inventors_list_general = []

uls = content.find_all("ul") if content else []

for ul in uls:
    for li in ul.find_all("li"):
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
        full_text = li.get_text()
        inventors_list.append((full_text))


del inventors_list_general[0:28]
del inventors_list_general[1073:]
del inventors_list[341:]



def separar_y_guardar(variable_lista, archivo_csv):
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Year"]+["Name of invention"]) 
        
        for item in variable_lista:
            partes = item.split(":", 1) 
            writer.writerow([partes[0]]+[partes[1]]) 

def separar_y_guardar2(variable_lista, archivo_csv):
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Year"]+["Inventions"]) 
        
        for item in variable_lista:
            partes = item.split(",", 1) 
            if len(partes)==2:
                writer.writerow([partes[0]]+[partes[1]]) 
            else:
                writer.writerow(partes) 

separar_y_guardar(inventors_list, "inventors_list.csv")
separar_y_guardar2(inventors_list_general, "inventors_list_general.csv")


#print(inventors_list[0])
#print(inventors_list_general[0])
