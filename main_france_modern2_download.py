import pandas as pd
from helpers import download_urls


# Download AN data
an_pdf_savepath = 'data/work/france/5th_rep/an_pdf/'
an_html_savepath = 'data/work/france/5th_rep/an_html/'
an_sitting_urls = pd.read_csv('data/work/france/5th_rep/an12-15_metadata_urls.csv')
download_urls(an_sitting_urls['pdf'], an_pdf_savepath)
download_urls(an_sitting_urls['html'], an_html_savepath)


# Download Senat data
senat_pdf_savepath = "data/work/france/5th_rep/senat_pdf/"
senat_html_savepath = "data/work/france/5th_rep/senat_html/"
senat_sitting_urls = pd.read_csv('data/work/france/5th_rep/senat_1996-2022_metadata_urls.csv', keep_default_na=False)
download_urls(senat_sitting_urls['pdf'][senat_sitting_urls['pdf'] != ''], senat_pdf_savepath)
download_urls(senat_sitting_urls['html'][senat_sitting_urls['html'] != ''], senat_html_savepath)
