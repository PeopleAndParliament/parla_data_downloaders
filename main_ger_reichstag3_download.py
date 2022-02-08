# Download Reichstag OCR files.

import csv
import requests
from tqdm import tqdm
import random
import time


def download_url(url, savepath, error_log):
    saveloc = savepath + "/" + url.split('/')[-2] + "_ocr_" + url.split('/')[-1] + ".html"
    time.sleep(random.randint(0, 2))
    resp = requests.get(url, timeout=20)
    if resp.status_code == 200:
        with open(saveloc, 'w') as f:
            f.write(resp.content.decode('utf-8'))
    else:
        with open(error_log, 'a') as f:
            f.write(url + "\n")


metadata_csv = 'data/work/germany/to_scrape.csv'
savepath = 'data/work/germany/ocr/'
errorlog = 'data/work/germany/ocr_download_errors.log'

files_to_dl = []
with open(metadata_csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        files_to_dl.append(row['ocr_url'])

for url in tqdm(files_to_dl):
    download_url(url, savepath, errorlog)
