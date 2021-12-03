# Senate 2003-2021 (xml): https://data.senat.fr/la-base-comptes-rendus/
# National Assembly 2017-2021 (xml): https://data.assemblee-nationale.fr/travaux-parlementaires/debats
# Senate pre-2003: http://www.senat.fr/seances/seances.html
# National Assembly pre-2007: https://archives.assemblee-nationale.fr/

import sys
from time import sleep
from bs4 import BeautifulSoup
import requests
from helpers import download_urls
from tqdm import tqdm


def get_month_urls(root_url):
    root_path = "/".join(root_url.split("/")[:-1]) + "/"
    resp = requests.get(root_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    search_str = "un seul fichier"
    text_links = bsoup.find_all("a", string=search_str)
    links = [root_path + x['href'] for x in text_links]
    return links


def get_senate_urls(root_url, start_year, end_year):
    resp = requests.get(root_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    seances_headers = ["Séances de " + str(x) for x in range(start_year, end_year + 1)]
    root_path = "/".join(root_url.split("/")[:-1]) + "/"
    links = []
    for seances_header in seances_headers:
        seances = bsoup.find("h3", string=seances_header).parent.findChildren("a")
        links.extend([root_path + x['href'] for x in seances])
    return links


# scrape the senate
savepath = "data/work/france/scraped/senate/"
senate_site = "http://www.senat.fr/seances/seances.html"
senate_urls = get_senate_urls(senate_site, 1996, 2002)
all_month_urls = []
for url in tqdm(senate_urls):
    all_month_urls.extend(get_month_urls(url))
download_urls(all_month_urls, savepath)


# scrape the national assembly
# up to 2002, pdf. after that, html:
an_urls = [
    "http://www.assemblee-nationale.fr/14/debats/index.asp",  # 2012 - 2017
    "http://www.assemblee-nationale.fr/13/debats/index.asp",  # 2007 - 2012
    "https://www.assemblee-nationale.fr/12/debats/index.asp",  # 2002 - 2007
]

