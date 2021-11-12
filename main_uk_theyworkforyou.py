import sys
from time import sleep
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from glob import glob


def get_file_urls(root_url):
    resp = requests.get(debates_url)
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


debates_url = "https://www.theyworkforyou.com/pwdata/scrapedxml/debates/"
members_url = "https://www.theyworkforyou.com/pwdata/scrapedxml/regmem/"

# debates_outpath = "data/work/uk/theyworkforyou/debates/"
debates_outpath = "/media/vvaara/My Passport/worktemp/uk_debates/"
# members_outpath = "data/work/uk/theyworkforyou/members/"
members_outpath = "/media/vvaara/My Passport/worktemp/uk_members/"

debates_urls = get_file_urls(debates_url)
members_urls = get_file_urls(members_url)

print("Downloading content from " + debates_url)
scrape_files(debates_urls, debates_outpath)
print("Downloading content from " + members_url)
scrape_files(members_urls, members_outpath)
