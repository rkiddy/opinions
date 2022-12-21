
import itertools
import pprint
import re
from time import sleep

import mysql.connector
import requests
from bs4 import BeautifulSoup

# human-readable: 'https://www.courts.ca.gov/opinions-nonpub.htm?Courts=Y'

# i-frame inside the page:
primary_url = 'https://www.courts.ca.gov/cms/npopinions.htm?Courts=Y'

url_head = 'https://www.courts.ca.gov'

mydb = mysql.connector.connect(
  host="localhost",
  user="ray",
  password="ZEKRET_WORD_HERE",
  database="ca_courts"
)

mo_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
mo_nums = [str(x).zfill(2) for x in range(1,13)]
mos = dict(zip(mo_names, mo_nums))

def fix_date(date_str):
    if re.match("[A-Z][a-z]{2} [0-9]{1,2}, [0-9]{4}", date_str):
        p = date_str.split(' ')
        mon = mos[p[0]]
        dt = p[1].replace(',', '').zfill(2)
        yr = p[2]
        return f"{yr}-{mon}-{dt}"
    else:
        return None

myc = mydb.cursor()

myc.execute("select max(pk) from opinions");
max_pk = myc.fetchone()[0]

if max_pk is None:
    next_pk = 1
else:
    next_pk = max_pk + 1

response = requests.get(primary_url)
soup = BeautifulSoup(response.content, 'html.parser')

cols = ['pk', 'filed_date', 'pdf_link', 'docx_link',
        'details_link', 'docket_num', 'short_name', 'opinion_type']

blanks = ', '.join(list(itertools.repeat('%s', len(cols))))
sql = f"insert into opinions ({', '.join(cols)}) values ({blanks})"

pos = dict(zip(cols, range(0,len(cols))))

rows_added = 0

while soup is not None:
    for row in soup.find_all('tr'):

        data_row = list(itertools.repeat(None, len(cols)))

        for link in row.find_all('a'):
            if link is not None and link['href'] is not None:
                if link['href'].endswith("PDF"):
                    data_row[pos['pdf_link']] = f"{url_head}{link['href']}"
                if link['href'].endswith("DOCX"):
                    data_row[pos['docx_link']] = f"{url_head}{link['href']}"
                if 'https://appellatecases' in link['href']:
                    data_row[pos['details_link']] = f"{link['href']}"

        idx = 1
        for cell in row.find_all('td'):
            if cell.string is not None:
                value = f"{cell.string}"
            else:
                value = f"{cell.next_element}"
            if idx == 1:
                data_row[pos['filed_date']] = fix_date(value)
            if idx == 2:
                data_row[pos['docket_num']] = value
            if idx == 3:
                data_row[pos['short_name']] = value
            idx = idx + 1

        dnum = data_row[pos['docket_num']]

        if dnum is not None:

            count = myc.execute(f"select count(0) from opinions where docket_num = '{dnum}'")
            if myc.fetchone()[0] == 0:

                data_row[pos['pk']] = next_pk
                next_pk = next_pk + 1
                data_row[pos['opinion_type']] = 'Unpub/Uncite'

                print("inserting:")
                pprint.pprint(data_row, compact=True)
                myc.execute(sql, data_row)
                mydb.commit()

                rows_added = rows_added + 1

    next_page = None

    for para in soup.find_all('p'):
        if para.a is not None:
            if para.a.string == 'Next page >>':
                next_page = para.a['href']

    if next_page is None:
        soup = None
    else:

        response = requests.get(f"{url_head}{next_page}")
        soup = BeautifulSoup(response.content, 'html.parser')
        sleep(3)

print(f"\nrows added: {rows_added}\n")

