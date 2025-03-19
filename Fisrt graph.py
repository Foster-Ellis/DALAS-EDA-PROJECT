import pandas as pd
import matplotlib.pyplot as plt

archivo = "Book(Hoja1).csv"

df = pd.read_csv(archivo, encoding='latin-1')

columna_numeros = df.iloc[:, 2]

conteo = columna_numeros.value_counts().sort_index()

conteo = conteo[(conteo.index >= 1280) & (conteo.index <= 2021)]

plt.figure(figsize=(12, 6))
plt.bar(conteo.index, conteo.values, color='b', alpha=0.7)

plt.xticks(range(1280, 2021, 15), rotation=45)

plt.xlabel("Years")
plt.ylabel("Inventions quantity")
plt.title("Inventions per year")
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()
