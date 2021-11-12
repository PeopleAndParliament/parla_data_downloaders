import sys
from time import sleep
from bs4 import BeautifulSoup
import requests


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


def scrape_files(file_urls, savepath):
    for file_url in file_urls:
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

debates_outpath = "data/work/uk/theyworkforyou/debates/"
members_outpath = "data/work/uk/theyworkforyou/members/"

debates_urls = get_file_urls(debates_url)
members_urls = get_file_urls(members_url)

scrape_files(debates_urls, debates_outpath)
scrape_files(members_urls, members_outpath)
