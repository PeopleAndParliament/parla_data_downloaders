import sys
from time import sleep
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from glob import glob


def get_file_urls(root_url):
    resp = requests.get(root_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    links = bsoup.find_all('a')
    link_urls = []
    for link in links:
        link_href = link.get('href')
        if link_href[-4:] == ".xml":
            link_urls.append(root_url + link_href)
    return link_urls


def scrape_files(file_urls, savepath, skip_downloaded=True):
    if skip_downloaded:
        urls_to_download = []
        files_present = glob(savepath + "*.xml")
        check_against = []
        for file in files_present:
            check_against.append(file.split("/")[-1])
        for file_url in file_urls:
            if file_url.split("/")[-1] in check_against:
                continue
            else:
                urls_to_download.append(file_url)
    else:
        urls_to_download = file_urls
    #
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


commons_url = "https://www.theyworkforyou.com/pwdata/scrapedxml/debates/"
commons_wmhall_url = "https://www.theyworkforyou.com/pwdata/scrapedxml/westminhall/"
lords_url = "https://www.theyworkforyou.com/pwdata/scrapedxml/lordspages/"

commons_outpath = "../data/raw/uk/theyworkforyou/commons_debates/"
wmhall_outpath = "../data/raw/uk/theyworkforyou/commons_wmhall/"
lords_outpath = "../data/raw/uk/theyworkforyou/lords_debates/"


commons_urls = get_file_urls(commons_url)
wmhall_urls = get_file_urls(commons_wmhall_url)
lords_urls = get_file_urls(lords_url)

print("Downloading content from " + commons_url)
scrape_files(commons_urls, commons_outpath)
print("Downloading content from " + lords_url)
scrape_files(lords_urls, lords_outpath)
print("Downloading content from " + commons_wmhall_url)
scrape_files(wmhall_urls, wmhall_outpath)
