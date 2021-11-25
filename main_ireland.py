from requests import get
import sys
from time import sleep
import json
from zipfile import ZipFile
from io import BytesIO
from tqdm import tqdm


class OireachtasAPIClient(object):
    def __init__(self):
        self.base_address = "https://api.oireachtas.ie/v1"

    def announce_query(self, api_request):
        print("Querying API with: " + api_request)

    def get_debates_meta(self, year):
        debates_address = self.base_address + "/debates?"
        get_parameters = (
            "limit=10000" +
            "&date_start=" + str(year) + "-01-01" +
            "&date_end=" + str(year) + "-12-31"
            )
        response = self.get_api_response(debates_address, get_parameters)
        return response

    def get_api_response(self, get_address,
                          get_parameters,
                          max_retries=20):
        retries = 0
        get_request = get_address + get_parameters
        while retries < max_retries:
            try:
                self.announce_query(get_request)
                response = get(get_request)
                data = response.json()
            except ValueError as error:
                print("  !> Request probably timed out or something." +
                      " Retrying in 8 secs. Retries: " + str(retries) + "/" +
                      str(max_retries))
                sleep(8)
                retries += 1
                if retries == max_retries:
                    sys.exit("  !!> Max retries reached for request.")
                continue
            else:
                break
        return data


def get_debate_urls(api_response):
    xml_urls = []
    for result in api_response['results']:
        xml_url = result['debateRecord']['formats']['xml']['uri']
        debate_uri = result['debateRecord']['uri']
        house_uri = result['debateRecord']['house']
        xml_urls.append({
            'xml_url': xml_url,
            'debate_uri': debate_uri,
            'house_uri': house_uri
        })
    return xml_urls


def get_debate_xml(xml_url, max_retries=10):
    retries = 0
    get_request = xml_url
    while retries < max_retries:
        try:
            response = get(get_request)
        except ValueError as error:
            print("  !> Request probably timed out or something." +
                  " Retrying in 8 secs. Retries: " + str(retries) + "/" +
                  str(max_retries))
            sleep(3)
            retries += 1
            if retries == max_retries:
                sys.exit("  !!> Max retries reached for request.")
            continue
        else:
            break
    return response.content.decode('utf-8')


def create_zip(debate_urls, this_year, downloads_delay=1):
    archive = BytesIO()
    with ZipFile(archive, 'w') as zip_archive:
        # Create three files on zip archive
        for this_debate in tqdm(debate_urls):
            this_xml = get_debate_xml(this_debate['xml_url'])
            outfname = this_debate['debate_uri'][8:].replace('/', '#') + ".xml"
            this_debate['file'] = outfname
            with zip_archive.open(outfname, 'w') as outf:
                outf.write(this_xml.encode('utf-8'))
            if downloads_delay > 0:
                sleep(downloads_delay)
        metadata_jsonfname = "metadata_" + str(this_year) + ".json"
        with zip_archive.open(metadata_jsonfname, 'w') as jsonout:
            jsondata = json.dumps(debate_urls, indent=4)
            jsonout.write(jsondata.encode('utf-8'))
    return archive


if __name__ == '__main__':

    api_client = OireachtasAPIClient()
    all_years = range(2014, 2021)

    for this_year in all_years:
        api_response = api_client.get_debates_meta(this_year)
        debate_urls = get_debate_urls(api_response)
        archive = create_zip(debate_urls, this_year, downloads_delay=0)
        # Flush archive stream to a file on disk
        with open('data/final/ireland/' + str(this_year) + '_ireland_debates.zip', 'wb') as f:
            f.write(archive.getbuffer())
