# Senate 2003-2021 (xml): https://data.senat.fr/la-base-comptes-rendus/
# National Assembly 2017-2021 (xml): https://data.assemblee-nationale.fr/travaux-parlementaires/debats
# Senate pre-2003: http://www.senat.fr/seances/seances.html
# National Assembly pre-2007: https://archives.assemblee-nationale.fr/
import pandas as pd
from bs4 import BeautifulSoup
import requests
from helpers import download_urls
from tqdm import tqdm
import re


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


def get_an_pdf_link(html_link):
    start_part = html_link.split('/cri/')[0]
    mid_part = '/pdf/cri/'
    end_part = html_link.split('/cri/')[-1].split('.')[0] + '.pdf'
    return start_part + mid_part + end_part


def get_month_number(month_string):
    month_string = month_string.replace('er ', '').lower()
    months = {
        'janvier': 1, 'erjanvier': 1, 'jan vier': 1,
        'février': 2, 'fevrier': 2, 'lévrier': 2, 'levrier': 2, 'fevrieï': 2, 'erfevrier': 2,
        'mars': 3, 'murs': 3, 'mai s': 3, 'mais': 3,
        'avril': 4, 'avrit': 4,
        'mai': 5, 'mal': 5, 'lai': 5, 'mat': 5, 'er mai':5,
        'juin': 6, 'join': 6, 'juiit': 6, 'juiu': 6,
        'juillet': 7, 'juillel': 7, 'juîllot': 7,
        'août': 8, 'aout': 8,
        'septembre': 9, 'sep tembre': 9,
        'octobre': 10, 'tobre': 10,
        'novembre': 11, 'novembro': 11, 'xoveiuhre': 11, 'nôvembre': 11, 'no vambre': 11,
        'décembre': 12, 'decembre': 12, 'decembro': 12, 'dcceubre': 12, 'de cembre': 12, 'decem bre': 12,
        'deeemjl re': 12, 'cp septembre': 12
    }
    if month_string in months.keys():
        return str(months[month_string])
    else:
        return None


def fr_datestring_to_date(fr_datestring):
    # eg.: 'mercredi 4 octobre 2006'
    day_raw = fr_datestring.split()[-3]
    month_raw = fr_datestring.split()[-2]
    year_raw = fr_datestring.split()[-1]
    if day_raw == '1er':
        day_raw = '1'
    if not day_raw.isnumeric() or len(day_raw) > 2:
        exit('datestr, day error: ' + fr_datestring)
    if len(day_raw) == 1:
        day = '0' + day_raw
    else:
        day = day_raw
    month = get_month_number(month_raw)
    if month is None:
        exit('datestr, month error: ' + fr_datestring)
    if len(str(month)) == 1:
        month = '0' + str(month)
    else:
        month = str(month)
    if year_raw == '21003':
        year_raw = '2003'
    year_raw = year_raw.strip('.')
    if not year_raw.isnumeric() or len(year_raw) != 4:
        exit('datestr, year error: ' + fr_datestring)
    return f'{year_raw}-{month}-{day}'


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
    if root_year <= 2004:  # 12
        for a in bsoup.find_all("a", href=re.compile("#TopOfPage")):
            html_link = root_path + a['href'].split('#')[0]
            datetext = ' '.join(a.text.split())
            # some errors in the html, quick fix:
            if datetext == "Première séance du jeudi 9 décembre":
                date = '2004-12-09'
            elif datetext == "Deuxième séance du mercredi 6 juillet":
                date = '2005-07-06'
            else:
                date = fr_datestring_to_date(a.text)
            links.append({'html': html_link,
                          'pdf': get_an_pdf_link(html_link),
                          'date': date,
                          'seance': a.text.split('-')[-1].split(' du ')[0].strip(),
                          'legislature': html_link.split('/cri')[0].split('/')[-1],
                          'era': '5th_republic'})
    else:
        for h1 in bsoup.find_all("h1", class_="seance"):
            for a in h1.findChildren('a'):
                html_link = root_path + a['href']
                links.append({'html': html_link,
                              'pdf': get_an_pdf_link(html_link),
                              'date': fr_datestring_to_date(
                                  h1.find_previous('td', class_='date').text.strip()),
                              'seance': a.text.strip(),
                              'legislature': html_link.split('/cri')[0].split('/')[-1],
                              'era': '5th_republic'})
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


def get_an15_seances_page_session_links(an15_seances_page):
    base_url = an15_seances_page.split('/dyn')[0]
    resp = requests.get(an15_seances_page)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    seances = bsoup.find("ul", class_="crs-index-days")
    res = []
    for li in seances.find_all("li", recursive=False):
        seance_date = fr_datestring_to_date(li.find('h2', class_='crs-h-day').text)
        seances_container = li.find('ul', class_='crs-index-items')
        seances_single = seances_container.find_all('li', class_='crs-index-item')
        for ss in seances_single:
            seance = ss.find('h3', class_='crs-h-seance _colored')
            seance_text = seance.text.strip()
            seance_html = base_url + seance.find('a')['href']
            seance_pdf = base_url + ss.find('div', class_='button-list').find(
                'a', attrs={'data-tippy-content': "Télécharger le PDF"})['href']
            res.append({
                'html': seance_html,
                'pdf': seance_pdf,
                'date': seance_date,
                'seance': seance_text,
                'legislature': 15,
                'era': '5th_republic'})
    return res


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


# 1996 - 2002
def get_senate_month_urls(root_url):
    root_path = "/".join(root_url.split("/")[:-1]) + "/"
    resp = requests.get(root_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    search_str = "un seul fichier"
    text_links = bsoup.find_all("a", string=search_str)
    links = [root_path + x['href'] for x in text_links]
    ret = []
    #
    for link in links:
        date = link.split('/s')[-1].split('_mono')[0]
        date = date[0:4] + '-' + date[4:6] + '-' + date[6:]
        ret.append({
            'html': link,
            'pdf': '',
            'date': date,
            'era': '5th_republic'})
    return ret


def get_senate_month_urls2(root_url):
    root_path = "/".join(root_url.split("/")[:-1]) + "/"
    resp = requests.get(root_url)
    bsoup = BeautifulSoup(resp.text, 'html.parser')
    container_box = bsoup.find("div", class_="box-inner gradient-01")
    container_list = container_box.find('ul')
    for li in container_list.find_all('li', recursive=False):
        date = li.find('a', recursive=False).text.strip()
        print(date)
        html_link = li.find('ul', recursive=False).find('a', href=re.compile("_mono\.html"))
        print(root_path + html_link['href'])
        pdf_link = li.find('ul', recursive=False).find('a', href=re.compile("\.pdf"))
        print(root_path + pdf_link['href'])

    #
    for link in links:
        date = link.split('/s')[-1].split('_mono')[0]
        date = date[0:4] + '-' + date[4:6] + '-' + date[6:]
        ret.append({
            'html': link,
            'pdf': '',
            'date': date,
            'era': '5th_republic'})
    return ret


# no pdf - up to AVRIL 4/2005
# format 1. up to 12/2002
# format 2. from 1/2003 up to present day

# -------------------------------------
# scrape the senate
# -------------------------------------
# Quite straightforward, mostly consistent format.

# savepath = "data/work/france/scraped/senate/"

senate_site = "http://www.senat.fr/seances/seances.html"
senate_urls = get_senate_urls(senate_site, 1996, 2002)
all_month_urls = []
for url in tqdm(senate_urls):
    all_month_urls.extend(get_senate_month_urls(url))
#     date, html, pdf, era

# download_urls(all_month_urls, savepath)


# -------------------------------------
# the national assembly
# -
# urls and metadata
# -------------------------------------
# Get both pdf and html for AN12-15 and save those. Read the saved file
# to scrape actual contents.
# AN11 has also html, but is not covered here, but rather its pdfs are covered in
# main_france_5th_rep ...

# legislatures 12-14
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

# Actually there's only one ^. And the format changed with code revision, so let's
# overwrite that here instead of handling it neatly.
if len(all_sitting_urls) != 0:
    all_sitting_urls = [{'html': 'https://www.assemblee-nationale.fr/14/cri/congres/20154001.asp',
     'pdf': 'https://www.assemblee-nationale.fr/14/pdf/cri/congres/20154001.pdf',
     'date': '2015-11-16',
     'seance': 'Congrès du Parlement',
     'legislature': '14',
     'era': '5th_republic'}]

# get all sitting urls for each session, and add them to the few sitting urls mixed with session urls previously:
print('Get URLS and meta for AN11-14...')
for session_url in tqdm(session_urls):
    all_sitting_urls.extend(get_an_sitting_urls(session_url))

# an15
an15_seances_base = 'https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/seance'
an15_seances_urls = []
print('Get URLS and meta for AN15...')
for page_num in tqdm(range(1, 158)):
    an15page = (an15_seances_base + '?page=' + str(page_num))
    an15_seances_urls.extend(get_an15_seances_page_session_links(an15page))

# combine all an urls
all_sitting_urls.extend(an15_seances_urls)
an_urls_and_meta = pd.DataFrame(all_sitting_urls)
an_urls_and_meta.to_csv(
    'data/work/france/5th_rep/an12-15_metadata_urls.csv', index=False)


# todo:
# - senate: get url for pdf, html
# - download pdfs
#   - for dates with no pdf, create pdf-simulation from the html text
# - download html
# - add names for savefiles (or just use the names in pdf and html, they seem to be unique?)

# done:
# - save html-pdf-date-seance -metadata (add parliament number to that)

# an pdf
# available with similar paths to html files for legislature 12-14
# also 15.: https://www.assemblee-nationale.fr/15/debats/index.asp

# senat pdf
# missing for years between 1996 and 2005
