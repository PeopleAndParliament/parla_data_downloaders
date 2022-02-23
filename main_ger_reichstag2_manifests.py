import requests
import json
import dateutil.parser as dparser
import csv


# api example: https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00000010/manifest
# line 187 ->
# has both images, and ocr

# image: https://api.digitale-sammlungen.de/iiif/image/v2/bsb00000010_00262/full/full/0/default.jpg
# ocr: https://api.digitale-sammlungen.de/ocr/bsb00000010/262


def get_manifest_for_id(item_id):
    item_url = "https://api.digitale-sammlungen.de/iiif/presentation/v2/" + item_id + "/manifest"
    response = requests.get(item_url)
    data = response.json()
    return data


def get_sitzung_range(structures):
    first_sitzung_i = 0
    for i in range(0, len(structures)):
        if type(structures[i]['label']) is dict:
            label_s = structures[i]['label']['@value']
        elif type(structures[i]['label']) is list:
            label_s = structures[i]['label'][0]['@value']
        if 'sitzung' in label_s.lower():
            first_sitzung_i = i
            break
    last_sitzung_i = 0
    thislist = list(range(0, len(structures)))
    thislist.reverse()
    for i in thislist:
        if type(structures[i]['label']) is dict:
            label_s = structures[i]['label']['@value']
        elif type(structures[i]['label']) is list:
            label_s = structures[i]['label'][0]['@value']
        if 'sitzung' in label_s.lower():
            last_sitzung_i = i
            break
    return structures[first_sitzung_i:last_sitzung_i + 1]


def get_structure_date(structure):
    if type(structure['label']) is dict:
        label_s = structure['label']['@value']
    elif type(structure['label']) is list:
        label_s = structure['label'][0]['@value']
    date = None
    for item in label_s.split():
        if sum(c.isdigit() for c in item) > 6:
            date = dparser.parse(item, fuzzy=True, dayfirst=True)
            break
    if date is None:
        return None
    return date.strftime('%Y-%m-%d')


def get_canvases(sequences):
    final_canvases = dict()
    for sequence in sequences:
        for canvas in sequence['canvases']:
            canvas_n = int(canvas['@id'].split('/')[-1])
            canvas_img = canvas['images'][0]['resource']['@id']
            canvas_ocr = canvas['seeAlso']['@id']
            final_canvases[canvas_n] = {'img': canvas_img, 'ocr': canvas_ocr}
    return final_canvases


def get_final_structures(structures, canvases):
    # Set final format for structures, filter out structures that do not have 'sitzung' in label.
    # Other structures are needed in the process to get page ranges for the 'sitzung' structures, as
    # non-sitzung structures, such as lists of participants appear in between sitzung -pages.
    final_structures = list()
    for structure in structures:
        # Some structures do not have sitzungs at all, and therefore no canvases. Skip these.
        if 'canvases' not in structure.keys():
            continue
        label = None
        if type(structure['label']) is dict:
            label = structure['label']['@value']
        elif type(structure['label']) is list:
            label = structure['label'][0]['@value']
        is_sitzung = 'sitzung' in label.lower()
        if is_sitzung:
            date = get_structure_date(structure)
        else:
            # Few sitzungs do not have date in the label. Handle these later.
            date = None
        first_canvas_i = int(structure['canvases'][0].split("/")[-1])
        final_structures.append({
            'label': label,
            'date': date,
            'is_sitzung': is_sitzung,
            'first_canvas_i': first_canvas_i})
    # set last canvas i (end of range for canvases (=pages) for each subsection)
    for i in range(1, len(final_structures)):
        if i == len(final_structures) - 1:
            final_structures[i]['last_canvas_i'] = max(canvases.keys())
        final_structures[i - 1]['last_canvas_i'] = final_structures[i]['first_canvas_i'] - 1
    final_sitzung_structures = list()
    # filter out non-sitzungs, add canvases to structures
    for structure in final_structures:
        if structure['is_sitzung']:
            structure['canvases'] = dict()
            for key in canvases.keys():
                if key in range(structure['first_canvas_i'], structure['last_canvas_i'] + 1):
                    structure['canvases'][key] = canvases[key]
            final_sitzung_structures.append(structure)
    return final_sitzung_structures


def get_item_first_date(item):
    for entry in item['content']:
        if entry['date'] is None:
            continue
        else:
            return entry['date']
    return None


with open("data/work/germany/reichstag_data.json", 'r') as jsonfile:
    ids = json.load(jsonfile)

all_items = []
for this_id in ids:
    item_id = this_id['items'][0]['id']
    print(item_id)
    manifest = get_manifest_for_id(item_id)
    label = manifest['label']
    manifest_url = manifest['@id']
    canvases = get_canvases(manifest['sequences'])
    structures = get_sitzung_range(manifest['structures'])
    final_structures = get_final_structures(structures, canvases)
    item_data = {
        'id': item_id,
        'manifest_url': manifest_url,
        'content': final_structures
    }
    all_items.append(item_data)

# Create a flat table from above. columns:
# book_id, manifest_url, sitzung_label, sitzung_date, sitzung_order,
# date_is_estimate (t/f), page_number, img_url, ocr_url


final_out = list()
for item in all_items:
    book_id = item['id']
    manifest_url = item['manifest_url']
    i = 0
    last_good_date = get_item_first_date(item)
    for entry in item['content']:
        sitzung_label = entry['label']
        if entry['date'] is not None:
            sitzung_date = entry['date']
            last_good_date = entry['date']
            date_is_estimate = False
        else:
            sitzung_date = last_good_date
            date_is_estimate = True
        sitzung_order = i
        i += 1
        for k, v in entry['canvases'].items():
            page_number = k
            img_url = v['img']
            ocr_url = v['ocr']
            final_out.append({
                'book_id': book_id,
                'manifest_url': manifest_url,
                'sitzung_label': sitzung_label,
                'date': sitzung_date,
                'date_is_estimate': date_is_estimate,
                'sitzung_order': sitzung_order,
                'page_number': page_number,
                'img_url': img_url,
                'ocr_url': ocr_url
            })


outfile = 'data/work/germany/reichstag_pages.csv'
with open(outfile, 'w') as csvfile:
    fieldnames = list(final_out[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in final_out:
        writer.writerow(row)



# loop final structures, download ocr.
# *ocr filename: bsb-id + "_ocr_" + pagenumber
# create manifest json:
# * book id
# * manifest url
# * final structures
# * ocr file locations


# look at "structures" -- shows book parts, and allows detecting different "sitzungs" and leaving out TOC, etc
# pages are listed at "sequences">"canvases" and within each "canvas" "seeAlso">"@id" points to the OCR and
# "images">[listitem]"resource">"@id" points to the image. Could also check if the resource is of image type by
# checking field: "@type": "dctypes:Image",

# functions to do:
# - download:
#   * download manifest
#   * download page ocr
# - process:
#   * get structure from manifest
#     - find parts to discard (toc, foreword, ...)
#     - get headings for sitzungs (order, dates)
# - process page OCR:
#   1. replace improperly encoded characters (Ã¤, &#x00AD;, Ã¶ÃŸ, Ã¶, Ã¼, â€ž, â€”â€”, ...)
#   2. combine ocr_lines within ocr_par to single block of text. Combine words back together when line ends with hyphen
#   3. combine ocr_par within ocr_blocks.
#   4. discard ocr_blocks from start and end if they are very short (header and footer) - can check bbox height
#   5. combine ocr blocks -> return single page text
# - page text fields: period, item, page, content, img_url, date, session