# DALAS-EDA-PROJECT

This repository contains our exploratory data analysis work for the DALAS class at Sorbonne Université. We collect, clean, and visualize data on scientific inventions and discoveries over time. The project is organized into three main parts: data scraping, data cleaning, and data visualization. Each part lives in its own folder under `src`, and the raw and processed data files are stored in `raw_data`.

In the `src/scrape_script` folder, we have two notebooks: `data_scrappe_balam.ipynb` and `data_scrappe_yann.ipynb`. The Balam notebook extracts data from some websites andPDF sources, while the Yann notebook scrapes tables, timeline blocks, and list items from three different websites. Each scraper writes its results into `raw_data/scrape_data` as CSV files.

The `src/clean_scripts` folder contains `data_clean.ipynb`. This notebook reads all raw CSV files, merges them into a single table, and applies a series of cleaning steps. We remove extra punctuation, standardize country names with a lookup mapping, generalize detailed invention categories into broader fields, normalize text fields for later deduplication, and then apply a fuzzy-matching algorithm to merge near-duplicate records. The final cleaned dataset is saved as `raw_data/clean_data/clean_data_dd.csv`.

Under `src/visualization_scripts`, there are two notebooks: `visual_script_balam.ipynb` and `visual_script_yan.ipynb`. These notebooks load the cleaned data and produce a variety of plots. We start with a bar chart of annual counts, add a rolling mean trend line, and then explore discoveries by country in sixty-year bins using bubble charts and heatmaps. We also examine category distributions with pie charts, perform event annotations on time series, compare before-and-after periods with statistical tests, and analyze decadal trends and correlations among top invention fields. Finally, we use PCA and hierarchical clustering to reveal patterns in country-category profiles.

You can reproduce the analysis by running the scraper notebooks first, then the data cleaning notebook, and finally the visualization notebooks. All Python dependencies are listed in `requirements.txt`. The raw source files and intermediate outputs are under `raw_data`, while the notebooks in `src` contain code and explanatory text. This structure makes it easy to follow each step of our data pipeline from scraping to final charts.


![alt text](assets/image.png)