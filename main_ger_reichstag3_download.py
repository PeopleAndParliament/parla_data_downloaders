# Download Reichstag OCR files.

import csv
import requests
from tqdm import tqdm
import random
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import os


def read_success_log(success_log):
    with open(success_log, 'r') as f:
        succeeded = [line.rstrip() for line in f]
    return succeeded


def download_url(url, savepath, error_log, success_log, skip_existing=True):
    saveloc = savepath + "/" + url.split('/')[-2] + "_ocr_" + url.split('/')[-1] + ".html"
    if skip_existing and os.path.exists(saveloc):
        pass
    else:
        time.sleep(random.randint(0, 2))
        s = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        resp = s.get(url)
        # resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            with open(saveloc, 'w') as f:
                f.write(resp.content.decode('utf-8'))
            with open(success_log, 'a') as f:
                f.write(url + "\n")
        else:
            with open(error_log, 'a') as f:
                f.write(url + "\n")


def add_old_meta_to_success_log(old_meta, success_log):
    urls = []
    with open(old_meta, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            urls.append(row['ocr_url'])
    with open(success_log, 'a') as f:
        for url in urls:
            f.write(url + "\n")


old_meta = 'data/work/germany/reichstag_pages_old.csv'
metadata_csv = 'data/work/germany/reichstag_pages.csv'
savepath = 'data/final/germany/ocr/'
errorlog = 'data/work/germany/ocr_download_errors.log'
successlog = 'data/work/germany/ocr_download_completed.log'
# add_old_meta_to_success_log(old_meta, successlog)
completed_downloads = set(read_success_log(successlog))


files_to_dl = []
with open(metadata_csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['ocr_url'] not in completed_downloads:
            files_to_dl.append(row['ocr_url'])

for url in tqdm(files_to_dl):
    download_url(url, savepath, errorlog, successlog)
