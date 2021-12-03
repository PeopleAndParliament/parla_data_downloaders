from tqdm import tqdm
import requests
import sys
from time import sleep


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
