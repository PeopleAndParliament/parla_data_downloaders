from requests import get
from tqdm import tqdm


def download_file(file_url, outpath):
    response = get(file_url)
    fname = response.url.split('/')[-1]
    savepath = outpath + '/' + fname
    with open(savepath, 'wb')as file:
        file.write(response.content)


if __name__ == '__main__':

    datafiles_kungliga = [
        "https://data.kb.se/datasets/2017/09/riksdagstryck/person-och-sakregister-1809-1970.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-adelsst%C3%A5ndet-1627-1866.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-bihang-mm-1810-1866.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-bondest%C3%A5ndet-1720-1866.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-borgarst%C3%A5ndet-1654-1866.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-pr%C3%A4stest%C3%A5ndet-1642-1866.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-riksdagsakter-1521-.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/st%C3%A5ndsriksdagen-riksdagsbeslut-1529-1812.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-ber%C3%A4ttelser-redog%C3%B6relser-frsrdg.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-bet%C3%A4nkanden-memorial-utl%C3%A5tanden.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-motioner.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-propositioner-skrivelser.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-protokoll.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-register.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-reglementen-sfs.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-riksdagens-f%C3%B6rfattningssamling-rfs.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-riksdagsskrivelser-rskr.zip",
        "https://data.kb.se/datasets/2017/09/riksdagstryck/tv%C3%A5kammarriksdagen-1867-1970-utredningar-kombet-sou.zip"
    ]

    datafiles_riksdagen = [
        "http://data.riksdagen.se/dataset/dokument/prot-2018-2021.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-2014-2017.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-2010-2013.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-2006-2009.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-2002-2005.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-1998-2001.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-1990-1997.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-1980-1989.xml.zip",
        "http://data.riksdagen.se/dataset/dokument/prot-1971-1979.xml.zip",
        "http://data.riksdagen.se/dataset/person/person.xml.zip",
        "http://data.riksdagen.se/dataset/person/Sagtochgjort.csv.zip"
    ]

    print("Downloading data from data.kb.se ...")
    for item in tqdm(datafiles_kungliga):
        download_file(item, 'data/final/sweden/kb_se/')

    print("Downloading data from data.riksdagen.se ...")
    for item in tqdm(datafiles_riksdagen):
        download_file(item, 'data/final/sweden/riksdagen_se/')
