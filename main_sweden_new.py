# sources:
# https://riksdagstryck.kb.se/tvakammarriksdagen.html
# https://riksdagstryck.kb.se/standsriksdagen.html

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
from helpers import download_url
import string


def get_link_date(link_date_string, year_str):
    link_dates = link_date_string.split('-')
    res_dates = list()
    for link_date in link_dates:
        link_date = link_date.strip()
        day = link_date.split()[0]
        if len(day) == 1:
            day = '0' + day
        months_dict = {
            'januari': '01',
            'februari': '02',
            'mars': '03',
            'april': '04',
            'maj': '05',
            'juni': '06',
            'juli': '07',
            'augusti': '08',
            'september': '09',
            'oktober': '10',
            'november': '11',
            'december': '12'
        }
        month = months_dict.get(link_date.split()[1])
        date_final_str = f"{year_str}-{month}-{day}"
        res_dates.append(date_final_str)
    ret_dict = {'date_from': res_dates[0],
                'date_to': res_dates[-1]}
    return ret_dict


def get_single_year_links(year_bs_item):
    item = year_bs_item
    year_str = item.get('id').split('collapse')[-1]
    item_links = item.find_all('li', {'class': 'list-group-item'})
    links = list()
    for item_link in item_links:
        link_text = item_link.text
        if link_text[:20].lower() == 'riksdagens protokoll':
            date_str = link_text.split('; [')[1].split(']')[0]
            chamber = link_text.split('....')[1].split('kammaren')[0].strip().lower().replace('ö', 'o')
            link_dates = get_link_date(date_str, year_str)
            res_dict = {
                'text': link_text,
                'chamber': chamber,
                'url': item_link.find('a').get('href')
            }
            for k, v in link_dates.items():
                res_dict[k] = v
            links.append(res_dict)
    return links


def get_listing_item_content(listing_item, stands=False):
    links_url = listing_item['url']
    links_bs = BeautifulSoup(requests.get(links_url).content, 'html.parser')
    document_links = links_bs.find('article').find_all('a')
    urls = [link.get('href') for link in document_links]
    xml_urls = [url for url in urls if url[-3:] == 'xml']
    if not stands:
        xml_urls = [xml_url for xml_url in xml_urls if xml_url.split('/')[-1][:4] == 'prot']
    final_urls = list()
    for item in xml_urls:
        if stands:
            pdf_url = item.replace('xml', 'pdf')
        else:
            pdf_url = item.replace('.xml', '.pdf').replace('/xml/', '/pdf/web/')
        item_dict = {
            'local_file': item.split('/')[-1],
            'xml_url': item,
            'pdf_url': pdf_url,
            'order': item.split('__')[-1].split('.')[0]}
        for key in ['text', 'chamber', 'date_from', 'date_to']:
            item_dict[key] = listing_item[key]
        final_urls.append(item_dict)
    return final_urls


# 1867-1919 (https://riksdagstryck.kb.se/tvakammarriksdagen.html)
ids_to_find = ["collapse" + str(x) for x in range(1867, 1920)]
tvakammar_main_url = "https://riksdagstryck.kb.se/tvakammarriksdagen.html"
html_data = requests.get(tvakammar_main_url).content
bsoup = BeautifulSoup(html_data, 'html.parser')
bsoup_ids = [bsoup.find('div', {'id': x}) for x in ids_to_find]

print('getting index pages')
all_links = list()
for item in tqdm(bsoup_ids):
    all_links.extend(get_single_year_links(item))

print('getting final links')
final_links = list()
for item in tqdm(all_links):
    final_links.extend(get_listing_item_content(item))

links_df = pd.DataFrame(final_links)
links_df.to_csv('data/work/sweden/tvakammar1867-1919_links_and_meta.csv', index=False)

print('downloading XML files')
for item in tqdm(final_links):
    download_url(
        url=item['xml_url'],
        savepath='data/work/sweden/riksdagen_se_1867-1919',
        savename=item['local_file'],
        error_log='data/work/sweden/rd1867-1919.err',
        success_log='data/work/sweden/rd1867-1919.log',
        sleep=True)


# Ståndsriksdagen 1521-1866 (https://riksdagstryck.kb.se/standsriksdagen.html)

def stands_item_include(stands_item):
    it = stands_item.text.lower().translate(str.maketrans('', '', string.punctuation))
    if it.split()[0] in [
        'register', 'bihang', 'supplement', 'bilagor', 'supplementband',
        'tabeller', 'förtekning', 'förteckning', 'riksens',
        'statsutskottets', 'konstitutionsutskottets']:
        return False
    if it.split()[1] in ['register', 'bihang']:
        return False
    true_words = ['protocoll', 'protokoll', 'protokoller', 'protocoller',
                  'riksdagsprotokoll']
    if [word for word in true_words if word in it.split()]:
        return True
    return False


def get_stands_dates(stands_year_str):
    years = stands_year_str.split('-')
    if len(years) < 2:
        return {
            'date_from': years[0] + '-01-01',
            'date_to': years[0] + '-12-31'}
    else:
        return {
            'date_from': years[0] + '-01-01',
            'date_to': years[1] + '-12-31'}


def get_stands_chamber(link_text):
    if 'borgar' in link_text.lower():
        return 'borgerskap'
    if 'bonde' in link_text.lower():
        return 'bönder'
    if 'präste' in link_text.lower():
        return 'präster'
    if 'prest' in link_text.lower():
        return 'präster'
    if 'adel' in link_text.lower():
        return 'adel'
    return 'unknown'


def get_stands_collapse_items(stands_collapse):
    collapse_links = stands_collapse.find_all('li', {'class': 'list-group-item'})
    links = list()
    for item_link in collapse_links:
        if not stands_item_include(item_link):
            continue
        link_text = item_link.text
        link_dates = get_stands_dates(stands_collapse.get('id').split('collapse')[-1])
        res_dict = {
            'text': link_text,
            'chamber': get_stands_chamber(link_text),
            'url': item_link.find('a').get('href')
        }
        for k, v in link_dates.items():
            res_dict[k] = v
        links.append(res_dict)
    return links


stands_main_url = "https://riksdagstryck.kb.se/standsriksdagen.html"
stands_html_data = requests.get(stands_main_url).content
stands_bsoup = BeautifulSoup(stands_html_data, 'html.parser')
stands_container = stands_bsoup.find('div', {'id': 'accordion'})
stands_collapses = stands_container.find_all('div', {'class': 'panel-collapse'})

print('getting index pages')
stands_all_links = list()
for item in tqdm(stands_collapses):
    stands_all_links.extend(get_stands_collapse_items(item))

print('getting final links')
stands_final_links = list()
for item in tqdm(stands_all_links):
    stands_final_links.extend(get_listing_item_content(item, stands=True))

stands_links_df = pd.DataFrame(stands_final_links)
stands_links_df.to_csv('data/work/sweden/standsriksdagen_1521-1866_links_and_meta.csv', index=False)

print('downloading XML files')
for item in tqdm(stands_final_links):
    download_url(
        url=item['xml_url'],
        savepath='data/work/sweden/standsriksdagen',
        savename=item['local_file'],
        error_log='data/work/sweden/standsriksdagen.err',
        success_log='data/work/sweden/standsriksdagen.log',
        sleep=True)

