# Senate 2003-2021 (xml): https://data.senat.fr/la-base-comptes-rendus/
# National Assembly 2017-2021 (xml): https://data.assemblee-nationale.fr/travaux-parlementaires/debats
# Senate pre-2003: http://www.senat.fr/seances/seances.html
# National Assembly pre-2007: https://archives.assemblee-nationale.fr/

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


def get_sessions_11(an_url):
    root_path = "/".join(an_url.split("/")[:3])
    resp = requests.get(an_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for a in bsoup.find("ul", id="menu_cri").findChildren('a'):
        if "/11/cri/" in a['href']:
            links.append(root_path + a['href'])
    return links


def get_sessions_12(an_url):
    root_path = "/".join(an_url.split("/")[:3])
    resp = requests.get(an_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for a in bsoup.find("ul", id="menu_cri").findChildren('a'):
        if "/12/cri/" in a['href']:
            links.append(root_path + a['href'])
    return links


def get_an_session_links(an_urls):
    all_links = []
    for an_url in an_urls:
        if "/11/" in an_url:
            links = get_sessions_11(an_url)
        elif "/12/" in an_url:
            links = get_sessions_12(an_url)
        else:
            root_path = "/".join(an_url.split("/")[:3])
            resp = requests.get(an_url)
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
    for item in session_urls:
        if item[-4:] == ".asp":
            sitting_urls.append(item)
        else:
            filtered_session_urls.append(item)
    return {
        'sitting_urls': sitting_urls,
        'session_urls': filtered_session_urls
    }


def get_an_sitting_urls(session_url):
    if session_url[-1] != "/":
        session_url += "/"
    root_path = "/".join(session_url.split("/")[:-1]) + "/"
    resp = requests.get(session_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    if '14/cri/congres/' in root_path:
        root_year = int(root_path.split("/")[-1][:4])
    elif '13/budget/plf2008/' in root_path:
        root_year = 2008
    else:
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


def get_an11_sitting_urls(url_base_and_len):
    url_base = url_base_and_len['url']
    last_item_i = url_base_and_len['len']
    sitting_urls = []
    for i in range(1, last_item_i + 1):
        str_i = str(i)
        while len(str_i) < 4:
            str_i = "0" + str_i
        sitting_urls.append(url_base + str_i + ".asp")
    return sitting_urls


def get_an11_sitting_urls_to_download(sitting_url):
    # text after threshold are split page by page. download them with get_an11_later_sitting_page_urls()
    threshold = "20010107"
    sitting_index = sitting_url.split("/")[-1].split(".")[0]
    paginated = threshold <= sitting_index
    if paginated:
        page_urls = get_an11_later_sitting_page_urls(sitting_url)
        return page_urls
    else:
        return [sitting_url]


def get_an11_later_sitting_page_urls(sitting_url):
    # sitting: "https://www.assemblee-nationale.fr/11/cri/html/20020001.asp"
    # page: "https://www.assemblee-nationale.fr/11/cri/html/20020001/css/20020001_2.asp"
    pages_root = sitting_url[:-4] + "/css/" + sitting_url[:-4].split("/")[-1] + "_"
    pages_index_url = pages_root + "index.asp"
    filetype = ".asp"
    resp = requests.get(pages_index_url)
    if resp.status_code == 404:
        pages_index_url = pages_root + "index.htm"
        filetype = ".htm"
        resp = requests.get(pages_index_url)
    first_page = int(resp.text.split("gFirstPage =")[-1].split(";")[0].strip())
    last_page = int(resp.text.split("gLastPage =")[-1].split(";")[0].strip())
    pages_urls = []
    for i in range(first_page, last_page + 1):
        pages_urls.append(pages_root + str(i) + filetype)
    return pages_urls


# -------------------------------------
# scrape the senate
# -------------------------------------
# Quite straightforward, mostly consistent format.

savepath = "data/work/france/scraped/senate/"
senate_site = "http://www.senat.fr/seances/seances.html"
senate_urls = get_senate_urls(senate_site, 1996, 2002)
all_month_urls = []
for url in tqdm(senate_urls):
    all_month_urls.extend(get_month_urls(url))
download_urls(all_month_urls, savepath)


# -------------------------------------
# scrape the national assembly
# -------------------------------------

# up to 2002, pdf. after that, html. AN11 (1998-2002) is a special case, with format varying from year to year.

an_urls = [
    "http://www.assemblee-nationale.fr/14/debats/index.asp",  # 2012 - 2017
    "http://www.assemblee-nationale.fr/13/debats/index.asp",  # 2007 - 2012
    "https://www.assemblee-nationale.fr/12/debats/index.asp",  # 2002 - 2007
]

session_links = get_an_session_links(an_urls)
# there are some sitting urls already in the session links. the below only has the real session urls:
session_urls = filter_an_session_urls(session_links)['session_urls']
# there are some sitting urls already in the session links. these are filtered here:
all_sitting_urls = filter_an_session_urls(session_links)['sitting_urls']

# get all sitting urls for each session, and add them to the few sitting urls mixed with session urls previously:
for session_url in tqdm(session_urls):
    all_sitting_urls.extend(get_an_sitting_urls(session_url))

# an11 is a special case with format changing, etc.
# an11:
# from 1re SÉANCE DU 9 JANVIER 2001 onwards, format changes https://www.assemblee-nationale.fr/11/cri/html/20010107.asp
# 1998-1999: 0001-0295
# 1999-2000: 0001-0244
# 2000-2001: 0001-0224 --new format from(including): 0107
# 2001-2002: 0001-0143

url_bases_an11 = [
    {'url': "https://www.assemblee-nationale.fr/11/cri/html/2002", 'len': 143},
    {'url': "https://www.assemblee-nationale.fr/11/cri/html/2001", 'len': 224},
    {'url': "https://www.assemblee-nationale.fr/11/cri/html/2000", 'len': 244},
    {'url': "https://www.assemblee-nationale.fr/11/cri/html/1999", 'len': 295}
]

all_sitting_urls_an11 = list()
for url_and_len in url_bases_an11:
    # get list of sitting urls. Some are broken into separate pages, so they need to be checked
    an11_sitting_urls = get_an11_sitting_urls(url_and_len)
    # check each sitting url, if above certain threshold, they are paginated and the page urls need to be added
    for sitting_url in tqdm(an11_sitting_urls):
        urls_to_download = get_an11_sitting_urls_to_download(sitting_url)
        all_sitting_urls_an11.extend(urls_to_download)

all_sitting_urls.extend(all_sitting_urls_an11)

an_savepath = "data/work/france/scraped/an/"
download_urls(all_sitting_urls, an_savepath)
