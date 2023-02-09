'''
This version demonstrates a few more advanced techniques -- inline comments are mainly for stuff not covered in the basic script:
- Separation of concerns: Writing a function to handle each task -- downloading the page and scraping the data -- and setting up the script to allow those functions to be imported into other scripts, if that need should ever arise
- Doing a little more text processing to break the name into last/rest components, and to separate out terms of service, so now the atomic observation being written to file is a term of service, not a board member
- Using csv.DictWriter instead of csv.writer
- Demonstrating a few other useful Python techniques, such as list comprehensions, multiple assignment, star unpacking and custom list sorting
'''

import os
import csv

import requests
from bs4 import BeautifulSoup


def download_page(url, html_file_out):

    if not os.path.exists(html_file_out):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'  # noqa
        }

        r = requests.get(
            url,
            headers=headers
        )

        r.raise_for_status()

        with open(html_file_out, 'w') as outfile:
            outfile.write(r.text)

        print(f'Downloaded {html_file_out}')

    return html_file_out


def parse_data(html_file_in, csv_file_out):
    with open(html_file_in, 'r') as infile:
        html = infile.read()

    soup = BeautifulSoup(
        html,
        'html.parser'
    )

    target_div = soup.find(
        'div',
        {'id': 'past-ire-board-members'}
    )

    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    members = [x.text.strip() for x in target_div.find_all('p')]

    csv_headers = [
        'name_last',
        'name_rest',
        'term_start',
        'term_end',
        'was_president',
        'is_deceased'
    ]

    # start an empty list to hold records to write
    parsed_member_data = []

    # loop over member text
    for member in members:

        was_president = False
        is_deceased = False

        if member.startswith('*'):
            was_president = True

        if '(dec)' in member:
            is_deceased = True

        # https://exercism.org/tracks/python/concepts/unpacking-and-multiple-assignment
        # https://docs.python.org/3/tutorial/controlflow.html?highlight=unpack#unpacking-argument-lists
        # here, the value attached to the `rest` var is ignored
        name, terms, *rest = member.split('(')

        name_clean = name.lstrip('*').strip()
        terms_clean = terms.split(')')[0]

        # split the name into last, rest
        name_split = name_clean.rsplit(' ', 1)

        # handle generational suffixes
        if name_split[-1] == 'Jr.':
            name_split = name_split[0].rsplit(' ', 1)
            name_split[0] += ' Jr.'
        
        rest, last = name_split

        # loop over the terms of service
        for term in terms_clean.split(','):
            term_start, term_end = term.strip().split('-')

            # create a dict by zipping together the headers with the list of data
            data = dict(zip(csv_headers, [
                last,
                rest,
                term_start,
                term_end,
                was_president,
                is_deceased
            ]))

            # add the dict to the main list
            parsed_member_data.append(data)

    # sort member data by last name, then first name, then term start
    data_sorted = sorted(
        parsed_member_data,
        key=lambda x: (
            x['name_last'],
            x['name_rest'],
            x['term_start']
        )
    )

    # write to file, specifying the encoding and
    # dealing with a Windows-specific problem that
    # sometimes pops up when writing to file
    with open(csv_file_out, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=csv_headers
        )
        writer.writeheader()
        writer.writerows(data_sorted)

    print(f'Wrote {csv_file_out}')


# https://realpython.com/if-name-main-python/
if __name__ == '__main__':

    url = 'https://www.ire.org/about-ire/past-ire-board-members/'

    # https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals
    files_name = 'ire-board'
    filename_page = f'{files_name}.html'
    filename_csv = f'{files_name}-terms.csv'

    # call the functions
    download_page(url, filename_page)
    parse_data(filename_page, filename_csv)
