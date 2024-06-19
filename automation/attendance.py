import urllib.request
import pandas as pd
from datetime import date, datetime
import pandas as pd
import PyPDF2
from pdfminer.high_level import extract_text
import os
import glob

# PATH to the existing files
mp_session_15_file = r'hansard_malaysia\sessions\session_15\mp_session_15.csv'
attendance_file = r'hansard_malaysia\sessions\session_15\attendance_session_15.csv'

# # get today's date
# tdate = date.today()

# # request url for hansard, if available
# url_hansard = 'https://www.parlimen.gov.my/files/hindex/pdf/DR-' + tdate.strftime('%d%m%Y') +  '.pdf'
# today_hansard = requests.get(url_hansard)

# # exit the code if no hansard available
# if str(today_hansard.content) == "b'File does not exist (3)'":
#     print('No parliament seating on this date')
#     exit()

# get today's date
tdate = date(2024, 3, 11)

# request url for hansard, if available
print("Downloading newest hansard...")
url_hansard = 'https://www.parlimen.gov.my/files/hindex/pdf/DR-' + tdate.strftime('%d%m%Y') +  '.pdf'
urllib.request.urlretrieve(url_hansard, f'automation/hansard_' + 'DR-' + tdate.strftime('%d%m%Y') + '.pdf')

# open current records with pandas
mp = pd.read_csv(mp_session_15_file)
attendance_df = pd.read_csv(attendance_file)

# Create column for keyword search in hansard
mp = mp.iloc[:, :].astype("string")
mp['seat_search'] = ['(' + ''.join(area.split()).lower() + ')' for area in mp.seat.tolist()]

# Initiate dataframe with seat code for every mp in df
df = pd.DataFrame(columns=['date'] + mp.seat_code.tolist())

def find_MP(seat,string): return 1 if seat in string else 0

pdf_active = PyPDF2.PdfReader(open(f'automation/hansard_DR-' + tdate.strftime('%d%m%Y') + '.pdf' , 'rb', ),strict=False)
n_pages = len(pdf_active.pages)
extract_start = 0
start_set = 0
extract_end = 0
# create a for loop to find start and end page for MPs attendance
for page in range(n_pages):
    page_active = ''.join(pdf_active.pages[page].extract_text().split()).lower()
    if start_set == 0 and ('senaraikehadiran' in page_active or 'ahliyanghadir' in page_active):
        extract_start = page
        start_set = 1 # ensure first instance is taken and frozen
    if 'yangtidakhadir' in page_active: extract_end = page
    elif page > 9:
        extract_end = page
    if extract_start > 0 and extract_end > 0: break # break the moment we find the end of the section

# extracting the text
res = extract_text(f'automation/hansard_DR-' + tdate.strftime('%d%m%Y') + '.pdf', page_numbers=[x for x in range(extract_start,extract_end+1)])
res = ''.join(res.split()).lower()
res = res.replace('(johorbaru)','(johorbahru)')
res = res.replace('bentong)', '(bentong)')
hadir = res.split('yangtidakhadir')[0] #only get list name that attend

# find MP attendance
attendance = [find_MP(area,hadir) for area in mp.seat_search.tolist()]

# update the attendance record
formatted_date = tdate.strftime('%d/%#m/%Y')

if formatted_date not in attendance_df.columns:
    attendance_df.drop(columns='total', inplace=True)
    attendance_df[formatted_date] = attendance
    attendance_df['total'] = attendance_df.iloc[:, 3:].sum(axis=1)

    # save to file
    attendance_df.to_csv(attendance_file, index=False)
    print("Parliament attendance record updated!")
else:
    print("Record is up-to-date")