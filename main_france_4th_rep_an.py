import requests
from helpers import download_urls
from tqdm import tqdm
import re
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import random


base_url = "http://4e.republique.jo-an.fr/numero/"
years = list(range(1945, 1959))
savepath = 'data/work/france/4th_rep/'


def load_pdfs_for_year(year, savepath):
    year_index = 1
    missing_values = 0
    while missing_values < 5:
        this_req_url = base_url + str(year) + "_i" + str(year_index) + ".pdf"
        time.sleep(random.randint(0, 2))
        s = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        resp = s.get(this_req_url)
        # resp = requests.get(this_req_url)
        if resp.status_code == 404:
            missing_values += 1
        else:
            savefile = savepath + this_req_url.split("/")[-1]
            open(savefile, 'wb').write(resp.content)
            print(f"Saved {savefile}")
            missing_values = 0
        year_index += 1
        if missing_values == 5:
            print(f"Done for {str(year)}")


for year in years:
    load_pdfs_for_year(year, savepath)
