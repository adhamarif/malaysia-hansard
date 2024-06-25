import urllib.request
import pandas as pd
from datetime import date, timedelta
import PyPDF2
from pdfminer.high_level import extract_text
import os
import requests

# PATH to the existing files
mp_session_15_file = 'hansard_malaysia/sessions/session_15/mp_session_15.csv'
attendance_file = 'hansard_malaysia/sessions/session_15/attendance_session_15.csv'

# open current records with pandas
mp = pd.read_csv(mp_session_15_file)
attendance_df = pd.read_csv(attendance_file)

# Malaysian Parliament date. Check the seating period here --> https://www.parlimen.gov.my/takwim-dewan-rakyat.html?uweb=dr&
start_date = date(2024, 2, 26)
end_date = date(2024, 3, 27)

# Generate list of dates from start_date to end_date
date_list = [(start_date + timedelta(days=x)) for x in range((end_date - start_date).days + 1)]

for tdate in date_list:
    # request url for hansard, if available
    url_hansard = 'https://www.parlimen.gov.my/files/hindex/pdf/DR-' + tdate.strftime('%d%m%Y') +  '.pdf'
    today_hansard = requests.get(url_hansard)

    # exit the code if no hansard available
    if str(today_hansard.content) == "b'File does not exist (3)'":
        print(f'No parliament seating on: {tdate}')
        continue

    ### start scraping the pdf on the available pdfs
    # request url for hansard, if available
    print("Downloading newest hansard...")
    url_hansard = 'https://www.parlimen.gov.my/files/hindex/pdf/DR-' + tdate.strftime('%d%m%Y') +  '.pdf'
    pdf_path = f'automation/hansard_DR-' + tdate.strftime('%d%m%Y') + '.pdf'
    urllib.request.urlretrieve(url_hansard, pdf_path)

    # Create column for keyword search in hansard
    mp = mp.astype(str)
    mp['seat_search'] = ['(' + ''.join(area.split()).lower() + ')' for area in mp.seat.tolist()]

    # Initiate dataframe with seat code for every mp in df
    df = pd.DataFrame(columns=['date'] + mp.seat_code.tolist())

    def find_MP(seat, string): return 1 if seat in string else 0

    pdf_active = PyPDF2.PdfReader(open(pdf_path, 'rb'), strict=False)
    n_pages = len(pdf_active.pages)
    extract_start = 0
    start_set = 0
    extract_end = 0
    # create a for loop to find start and end page for MPs attendance
    for page in range(n_pages):
        page_active = ''.join(pdf_active.pages[page].extract_text().split()).lower()
        if start_set == 0 and ('senaraikehadiran' in page_active or 'ahliyanghadir' in page_active):
            extract_start = page
            start_set = 1  # ensure first instance is taken and frozen
        if 'yangtidakhadir' in page_active: extract_end = page
        elif page > 9:
            extract_end = page
        if extract_start > 0 and extract_end > 0: break  # break the moment we find the end of the section

    # extracting the text
    res = extract_text(pdf_path, page_numbers=[x for x in range(extract_start, extract_end + 1)])
    res = ''.join(res.split()).lower()
    res = res.replace('(johorbaru)', '(johorbahru)')
    res = res.replace('bentong)', '(bentong)')
    hadir = res.split('yangtidakhadir')[0]  # only get list name that attend

    # find MP attendance
    attendance = [find_MP(area, hadir) for area in mp.seat_search.tolist()]

    # update the attendance record
    formatted_date = tdate.strftime('%d/%-m/%Y')

    if formatted_date not in attendance_df.columns:
        attendance_df.drop(columns='total', inplace=True)
        attendance_df[formatted_date] = attendance
        attendance_df['total'] = attendance_df.iloc[:, 3:].sum(axis=1)

        # save to file
        attendance_df.to_csv(attendance_file, index=False)
        print(f"Parliament attendance record updated until {tdate}!")
    else:
        print("Record is up-to-date")
