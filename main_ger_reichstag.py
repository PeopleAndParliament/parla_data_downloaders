import requests
import json

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


with open("data/work/germany/reichstag_data.json", 'r') as jsonfile:
    ids = json.load(jsonfile)

item_id = ids[0]['items'][0]['id']

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