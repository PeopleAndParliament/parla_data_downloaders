import pandas as pd
from helpers import download_urls


an_pdf_savepath = 'data/work/france/5th_rep/an_pdf/'
an_html_savepath = 'data/work/france/5th_rep/an_html/'
# download urls separately, redo code below ...
an_sitting_urls = pd.read_csv('data/work/france/5th_rep/an12-15_metadata_urls.csv')
download_urls(an_sitting_urls['pdf'], an_pdf_savepath)
download_urls(an_sitting_urls['html'], an_html_savepath)


senat_pdf_savepath = "data/work/france/5th_rep/senat_pdf/"
senat_html_savepath = "data/work/france/5th_rep/senat_html/"

