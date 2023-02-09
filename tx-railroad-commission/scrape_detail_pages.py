import glob
import csv
import re
import os
from datetime import datetime

from bs4 import BeautifulSoup

from dl_pages_results import BASE_URL


csv_filepath = 'tx-railroad-commission-data.csv'

# set up headers for the CSV file
csv_headers = [
    'complaint_id',
    'complaint_url',
    'capture_method',
    'location',
    'city',
    'resolution_status',
    'complaint_type',
    'received_date',
    'business_area',
    'organization',
    'unit_name',
    'region',
    'regulated_entity',
    'p5_no',
    'jurisdictional',
    'regulated',
    'complaint_description_type',
    'complaint_description',
    'resolution_description',
    'complaint_comments',
    'update_notes',
    'close_date',
    'explanation_type',
    'explanation',
    'referral_type',
    'referred_to',
    'inspection_packages_link',
    'inspection_documents_link'
]

# get a list of HTML files in the detail pages dir
files = glob.glob('pages-detail/*.html')


# set up a reusable function to scrape data from
# a single HTML file
def scrape_page(html_path):

    # open the file and read in the HTML
    with open(html_path, 'r') as infile:
        html = infile.read()

    # turn the HTML into a bs4 object
    soup = BeautifulSoup(html, 'html.parser')

    # and start locating the elements using various bs4 methods
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/

    complaint_no = soup.find('span', text='Complaint Name').parent.next_sibling.text.split('-')[-1]

    url = f"{BASE_URL}/s/ietrs-complaint/{html_path.split('/')[-1].split('.html')[0]}/complaint{complaint_no}"

    capture_method = soup.find('span', text='Complaint Capture Method').parent.next_sibling.text.strip()

    location = soup.find('span', text='Complaint Location').parent.next_sibling.text.strip()

    resolution_status = soup.find('span', text='Complaint Resolution Status').parent.next_sibling.text.strip()

    complaint_type = soup.find('span', text=re.compile('Optional; If looking for a Railroad related option, this is not the correct jurisdiction')).parent.parent.next_sibling.text.strip()

    received_date = soup.find('span', text='Complaint Received Date').parent.next_sibling.text.strip()

    # additional integrity check for dates -- parse text as date
    received_date = datetime.strptime(
        received_date,
        '%m/%d/%Y'
    ).date().isoformat()

    business_area = soup.find('span', text='Business Area').parent.next_sibling.text.strip()

    city = soup.find('span', text='City').parent.next_sibling.text.strip()

    organization = soup.find('span', text='Organization').parent.next_sibling.text.strip()

    unit_name = soup.find('span', text='Unit Name').parent.next_sibling.text.strip()

    region = soup.find('span', text='Region').parent.next_sibling.text.strip()

    regulated_entity = soup.find('span', text='Regulated Entity').parent.next_sibling.text.strip()

    p5_no = soup.find('span', text='P5 #').parent.next_sibling.text.strip()

    jurisdictional = soup.find('span', text='Jurisdictional').parent.next_sibling.find('img').get('alt').strip()

    regulated = soup.find('span', text='Regulated').parent.next_sibling.text.strip()

    complaint_description_type = soup.find('span', text='Complaint Description Type').parent.next_sibling.text.strip()

    complaint_description = soup.find('span', text='Complaint Description').parent.next_sibling.text.strip()

    complaint_description = ' '.join(complaint_description.split())

    resolution_description = soup.find('span', text='Complaint Resolution Description').parent.next_sibling.text.strip()

    resolution_description = ' '.join(resolution_description.split())

    complaint_comments = soup.find('span', text='Complaint Comments').parent.next_sibling.text.strip()

    complaint_comments = ' '.join(resolution_description.split())

    update_notes = soup.find('span', text='Update Notes').parent.next_sibling.text.strip()

    update_notes = ' '.join(update_notes.split())

    close_date = soup.find('span', text='Complaint Close Date').parent.next_sibling.text.strip()

    # not every complaint has a close date
    if close_date:
        close_date = datetime.strptime(
            close_date,
            '%m/%d/%Y'
        ).date().isoformat()

    explanation_type = soup.find('span', text='Complaint Explanation Type').parent.next_sibling.text.strip()

    explanation = soup.find('span', text='Complaint Explanation').parent.next_sibling.text.strip()

    explanation = ' '.join(explanation.split())

    referral_type = soup.find('span', text='Complaint Referred Type').parent.next_sibling.text.strip()

    referred_to = soup.find('span', text='Complaint Referred To:').parent.next_sibling.text.strip()

    # joining a split string on a single space is
    # a way to remove all unnecessary whitespace
    referred_to = ' '.join(referred_to.split())

    inspection_packages = soup.find('span', {'title': 'Inspection Packages'})

    inspection_packages_link = f"{BASE_URL}{inspection_packages.parent.get('href')}"

    inspection_documents = soup.find('span', {'title': 'Inspection Documents'})

    inspection_documents_link = f"{BASE_URL}{inspection_documents.parent.get('href')}"

    # assemble the data in a list, maintaining
    # the same order as the CSV headers
    data = [
        complaint_no,
        url,
        capture_method,
        location,
        city,
        resolution_status,
        complaint_type,
        received_date,
        business_area,
        organization,
        unit_name,
        region,
        regulated_entity,
        p5_no,
        jurisdictional,
        regulated,
        complaint_description_type,
        complaint_description,
        resolution_description,
        complaint_comments,
        update_notes,
        close_date,
        explanation_type,
        explanation,
        referral_type,
        referred_to,
        inspection_packages_link,
        inspection_documents_link
    ]

    # return a dictionary representation of the data
    return dict(zip(csv_headers, data))


def scrape_data():
    # set up an empty list to hold the data to write to file
    all_data = []

    # loop over the list of files
    for file in files:

        # call the function to scrape this file
        # and assign to a variable the dictionary that the function returns
        data = scrape_page(file)

        # append the dictionary to the list we set up to
        # collect data from each page
        all_data.append(data)

    # open a file in write mode, specify the encoding and
    # set newlines='' to deal with windows-specific line breaks
    with open(csv_filepath, 'w', encoding='utf-8', newline='') as outfile:

        # set up the writer object
        writer = csv.DictWriter(
            outfile,
            fieldnames=csv_headers
        )

        # write the headers
        writer.writeheader()

        # write the data
        writer.writerows(all_data)

    return {
        'record_count': len(all_data),
        'filepath': csv_filepath
    }


if __name__ == '__main__':
    scrape_data()
    