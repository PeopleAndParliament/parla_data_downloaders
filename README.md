# parla_data_downloaders

Downloaders for various parliamentary datasets.

Python 3.8.10, libraries in `/requirements.txt`

## Ireland

main_ireland.py

## Sweden

main_sweden.py

## UK

main_uk_theyworkforus.py

Downloads the files for debates and members from [theyworkforyou](https://www.theyworkforyou.com/) .

Set parameters within the script:
* save path
* skip already downloaded content 

## Germany

Scripts for downloading the OCR and metadata from Bavarian State Library API.

* **main_ger_reichstag1_prep.py** gathers the ids of the books in the library API,
and some general metadata (title and collection) on them.
* **main_ger_reichstag2_manifests.py** requests the manifests (document metadata)
from the MDZ API, and collects relevant information (ocr and img url, more metadata)
for scraping to _data/work/germany/reichstag_pages.csv_ from the manifests.
* **main_ger_reichstag3_download.py** downloads the OCR pages (~18000),
logging the progress. Some basic error handling is included.

## France

### 5th Republic

This is in two parts, the old stuff and the modern/contemporary material.
The formats and storage methods change, so that's why.

#### More recent 5th Republic

* **main_france_modern1_urls_and_meta.py** - Gathers urls and metadata for both National assembly and the Senata and save those as csvs.
* **main_france_modern2_download.py** - Downloads the pdf and html urls listed in the csvs made by the above script.

#### Rest of the 5th Republic

Documentation TBD
