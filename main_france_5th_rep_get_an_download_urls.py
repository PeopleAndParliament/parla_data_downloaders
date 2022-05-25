import csv
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import lxml.html


def get_session_urls(session_urls_txt):
    with open(session_urls_txt, 'r') as f:
        res_items = dict()
        prev_key = None
        for line in f.readlines():
            line = line.strip()
            if line[:5] != "https":
                if line != "":
                    prev_key = line
                    res_items[prev_key] = list()
                else:
                    continue
            else:
                res_items[prev_key].append(line.strip())
    return res_items


def get_legislature_number(session_url):
    return int(session_url.split('/cri/')[0].split('/')[-1])


def get_session_type(session_url):
    raw_text = session_url.split('-')[-1].split('.')[0]
    session_type = ""
    for c in raw_text:
        if c.isalpha():
            session_type += c
    return session_type


def get_legislature_years(leg_header):
    return leg_header.split(" ")[-1].strip("(").strip(")")


def get_month_number(month_string):
    month_string = month_string.replace('er ', '')
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
        date_str = str(months[month_string])
        if len(date_str) == 1:
            date_str = '0' + date_str
        return date_str
    else:
        return None


def get_numeric_date(text_date):
    if text_date is None:
        return None
    if len(text_date.split()) != 4:
        return None
    day = text_date.split()[1]
    if len(day) == 1:
        day = '0' + day
    month = get_month_number(text_date.split()[2])
    year = text_date.split()[3]
    date_str = f'{year}-{month}-{day}'
    return date_str


def get_seance_numeric(seance_text):
    seances = {
        'Deuxième séance': 2,
        'Cinquième séance': 5,
        'Quatrième séance': 4,
        'Première séance': 1,
        'Troisième séance': 3,
        'Séance unique': 0}
    if seance_text in seances.keys():
        return seances[seance_text]
    else:
        return None


def get_pdf_urls(source_url, leg_header):
    #
    leg_num = get_legislature_number(source_url)
    leg_years = get_legislature_years(leg_header)
    session_type = get_session_type(source_url)
    #
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    resp = s.get(source_url)
    base_url = source_url.split('cri/')[0] + "cri/"
    #
    html = lxml.html.fromstring(resp.content)
    table = html.find(".//div[@class='prestableau']")
    rows = table.findall('.//tr')
    links_list = list()
    prev_date_text = None
    for row in rows:
        if len(row.findall('td')) < 1:
            continue
        date_text = row.find("td[@class='dateseance']")
        if date_text is not None:
            date_text = date_text.text_content().strip().replace(' 1er ', ' 1 ')
            prev_date_text = date_text
            date_is_estimate = False
        else:
            date_text = prev_date_text
            date_is_estimate = False
        row_links = row.findall("td[@class='seance']")
        for link in row_links:
            link_links = link.findall('a')
            for link_link in link_links:
                link_text = link_link.text.strip()
                link_href = base_url + link_link.attrib['href']
                savename = (link_href.split('nationale.fr/')[-1]).replace('/', '_')
                if savename[-4:] != '.pdf':
                    savename = None
                links_list.append({'date': get_numeric_date(date_text),
                                   'date_is_estimate': date_is_estimate,
                                   'seance': link_text,
                                   'seance_order': get_seance_numeric(link_text),
                                   'href': link_href,
                                   'legislature': leg_num,
                                   'session_type': session_type,
                                   'legislature_years': leg_years,
                                   'local_file': savename,
                                   'source_url': source_url})
    return links_list


an_pdf_roots_file = "data/raw/france/5th_rep_urls.txt"
session_urls = get_session_urls(an_pdf_roots_file)

links_list = list()
for k, v in session_urls.items():
    for session_url in v:
        print(session_url)
        links_list.extend(get_pdf_urls(session_url, k))

# manual corrections
manual_fixes = {
    'https://archives.assemblee-nationale.fr/8/cri/1987-1988-ordinaire2/001.pdf': {
        'date': '1988-04-02',
        'seance_order': '1'},
    'https://archives.assemblee-nationale.fr/8/cri/1985-1986-extraordinaire1/025.pdf':
        {'date': '1986-07-18'},
    'https://archives.assemblee-nationale.fr/8/cri/1985-1986-extraordinaire1/026.pdf':
        {'date': '1986-07-18'},
    'https://archives.assemblee-nationale.fr/4/cri/1968-1969-extraordinaire2/001.pdf':
        {'date': '1969-09-16'},
    'https://archives.assemblee-nationale.fr/4/cri/1968-1969-extraordinaire2/002.pdf':
        {'date': '1969-09-16'},
    'https://archives.assemblee-nationale.fr/4/cri/1968-1969-extraordinaire2/003.pdf':
        {'date': '1969-09-19'},
    'https://archives.assemblee-nationale.fr/4/cri/1968-1969-extraordinaire2/004.pdf':
        {'date': '1969-09-20'},
    'https://archives.assemblee-nationale.fr/0/cri/0-cri-1957-1958-001.pdf':
        {'session_type': 'ordinaire'},
    'https://archives.assemblee-nationale.fr/0/cri/0-cri-1957-1958-002.pdf':
        {'session_type': 'ordinaire'},
    'https://archives.assemblee-nationale.fr/0/cri/0-cri-1957-1958-003.pdf':
        {'session_type': 'ordinaire'},
    'https://archives.assemblee-nationale.fr/0/cri/0-cri-1957-1958-004.pdf':
        {'session_type': 'ordinaire'},
    'https://archives.assemblee-nationale.fr/0/cri/0-cri-1957-1958-005.pdf':
        {'session_type': 'ordinaire'},
}


for item in links_list:
    if item['href'] in manual_fixes.keys():
        for k, v in manual_fixes[item['href']].items():
            item[k] = v

links_list = sorted(links_list, key=lambda i: (i['date'], i['seance_order']))

outfile = 'data/work/france/5th_rep/an_pdf_url_metadata.csv'

with open(outfile, 'w') as outcsv:
    headers = list(links_list[0].keys())
    writer = csv.DictWriter(f=outcsv, fieldnames=headers)
    writer.writeheader()
    for item in links_list:
        writer.writerow(item)
