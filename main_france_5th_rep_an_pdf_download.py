import csv
from helpers import download_url
from helpers import read_success_log
from tqdm import tqdm


metadata_loc = 'data/work/france/5th_rep/an_pdf_url_metadata.csv'
successlog = 'data/work/france/5th_rep/pdf_download_completed.log'
errorlog = 'data/work/france/5th_rep/pdf_download_errors.log'
savepath = 'data/work/france/5th_rep/an_pdf'
completed_downloads = set(read_success_log(successlog))


# filter non-existing links.
# filter completed downloads.
files_to_dl = list()
with open(metadata_loc, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['local_file'] == '':
            continue
        if row['local_file'] not in completed_downloads:
            files_to_dl.append(row)


# download files
for file in tqdm(files_to_dl):
    download_url(
        url=file['href'],
        savepath=savepath,
        savename=file['local_file'],
        error_log=errorlog,
        success_log=successlog)
