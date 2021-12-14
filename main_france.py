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
import re


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

def get_sessions_12(an_url):
    root_path = "/".join(an_url.split("/")[:3])
    resp = requests.get(an_url, verify=False)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for a in bsoup.find("ul", id="menu_cri").findChildren('a'):
        if "/12/cri/" in a['href']:
            links.append(root_path + a['href'])
    return links


def get_an_session_links(an_urls):
    all_links = []
    for an_url in an_urls:
        if "/12/" in an_url:
            links = get_sessions_12(an_url)
        else:
            root_path = "/".join(an_url.split("/")[:3])
            resp = requests.get(an_url, verify=False)
            bsoup = BeautifulSoup(resp.text, 'html.parser')
            links = []
            for h1 in bsoup.find_all("h1", class_="section-main-title-alt"):
                for ul in h1.parent.findChildren('ul', class_="tabs-content"):
                    for a in ul.findChildren('a'):
                        link = root_path + a['href']
                        if "/cri/" in link:
                            links.append(link)
        all_links.extend(links)
    return all_links


def filter_an_session_urls(session_urls):
    sitting_urls = []
    filtered_session_urls = []
    for item in session_links:
        if item[-4:] == ".asp":
            sitting_urls.append(item)
        else:
            filtered_session_urls.append(item)
    return {
        'sitting_urls': sitting_urls,
        'session_urls': filtered_session_urls
    }


def get_an_sitting_urls(session_url):
    root_path = "/".join(session_url.split("/")[:-1]) + "/"
    resp = requests.get(session_url, verify=False)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    root_year = int(root_path.split("/")[-2].split("-")[0])
    links = []
    if root_year <= 2002:  # 12
        for a in bsoup.find_all("a", string=re.compile("Journaux Officiels")):
            links.append(root_path + a['href'].split('#')[0])
    elif root_year <= 2004:  # 12 later
        for a in bsoup.find_all("a", href=re.compile("#TopOfPage")):
            links.append(root_path + a['href'].split('#')[0])
    else:
        for h1 in bsoup.find_all("h1", class_="seance"):
            for a in h1.findChildren('a'):
                links.append(root_path + a['href'])
    return links


an_urls = [
    "http://www.assemblee-nationale.fr/14/debats/index.asp",  # 2012 - 2017
    "http://www.assemblee-nationale.fr/13/debats/index.asp",  # 2007 - 2012
    "https://www.assemblee-nationale.fr/12/debats/index.asp",  # 2002 - 2007
    "https://www.assemblee-nationale.fr/11/debats/index.asp",  # 1997 - 2002 (1997-1998 pdf, 1998-1999 -> html )
]

#  todo: cover 1997-2002 (11)

session_links = get_an_session_links(an_urls)

session_urls = filter_an_session_urls(session_links)['session_urls']
all_sitting_urls = filter_an_session_urls(session_links)['sitting_urls']

for session_url in session_links:
    all_sitting_urls.extend(get_an_sitting_urls(session_url))


