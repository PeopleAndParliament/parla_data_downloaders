from tqdm import tqdm
import requests
import sys
import time
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from os.path import exists


def read_success_log(success_log):
    if not exists(success_log):
        return []
    with open(success_log, 'r') as f:
        succeeded = [line.rstrip() for line in f]
    return succeeded


def download_urls(urls_to_download, savepath):
    for file_url in tqdm(urls_to_download):
        retries = 0
        max_retries = 10
        while retries < max_retries:
            try:
                response = requests.get(file_url)
                savefile = savepath + file_url.split("/")[-1]
                open(savefile, 'wb').write(response.content)
            except ValueError as error:
                print(error)
                print("  !> Request probably timed out or something." +
                      " Retrying in 2 secs. Retries: " + str(retries) + "/" +
                      str(max_retries))
                sleep(2)
                retries += 1
                if retries == max_retries:
                    sys.exit("  !!> Max retries reached for request.")
                continue
            else:
                break


def download_url(url, savepath, savename, error_log, success_log, sleep=False):
    saveloc = savepath + '/' + savename
    if sleep:
        time.sleep(random.randint(0, 2))
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    resp = s.get(url)
    if resp.status_code == 200:
        with open(saveloc, 'wb') as f:
            f.write(resp.content)
        with open(success_log, 'a') as f:
            f.write(url + "\n")
    else:
        with open(error_log, 'a') as f:
            f.write(url + "\n")
