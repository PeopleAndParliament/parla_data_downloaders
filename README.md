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
