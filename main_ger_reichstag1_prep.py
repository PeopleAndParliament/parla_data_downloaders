from lxml import etree
from glob import glob
import json

dfloc = "data/raw/ger_reichstag/rtbiauf_k3.html"
dfpath = "data/raw/ger_reichstag/"


def get_datafiles_dict(dfloc):
    with open(dfloc) as datafile:
        xml = datafile.read()
        xml = xml.replace("<br>", "")
    root = etree.fromstring(xml)
    header = " ".join(root.find('h1').text.strip().split())
    links = root.findall(".//a")
    ids = []
    for link in links:
        text = " ".join(link.text.split())
        id = link.attrib["href"].split("_")[-1].split(".")[0]
        ids.append({'id': id, 'text': text})
    return {'header': header, 'items': ids}


dflocs = glob(dfpath + "*.html")

all_dfs = []
for dfloc in dflocs:
    all_dfs.append(get_datafiles_dict(dfloc))

with open('data/work/germany/reichstag_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_dfs, f, ensure_ascii=False, indent=4)
