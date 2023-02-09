'''
In this script, we'll visit the South Dakota lobbyist registration lookup tool -- https://sosenterprise.sd.gov/BusinessServices/Lobbyist/LobbyistSearch.aspx -- an asp.net site that tracks user state and doesn't have consistent download paths for the lobbyist data files, because the files are generated on the fly based on search inputs. Therefore, we'll use playwright, a browser automation testing tool that's also handy for scraping websites.

The goal is to download each year's worth of lobbyist data for each type of lobbyist (private and public) and then assemble the results into a single data file.

The private lobbyist search has an "Export data" button, which kicks out a .zip file containing one pipe-delimited text file, but the public lobbyist search does not, so public lobbyist data will need to be scraped from the results table that appears below the search box.
'''

# we'll use this stdlib csv library to write out
# CSV files of the public lobbyist tables
import csv

# used for checking to see if files already exist
import os

# used for pausing between requests
import time

# we'll use this to calculate the current year
from datetime import date

# we'll use pandas to handle the zip files, since
# it can handle compressed files out the gate
import pandas as pd

# for getting wildcard references to local files
import glob

# playwright will run the browser
from playwright.sync_api import sync_playwright


# the URL where we want to start
URL = 'https://sosenterprise.sd.gov/BusinessServices/Lobbyist/LobbyistSearch.aspx'

# where the data files will land
DIR_DATA = 'data'

# the CSV file to write into
CSV_FILEPATH = 'sd-lobbyists.csv'

# grab the current year for comparison below
THIS_YEAR = date.today().year

# storing references to CSS selectors we'll use
# more than once below
LOCATOR_SELECT_YEAR = 'select#ctl00_MainContent_slctYears'
LOCATOR_SELECT_TABLE_LEN = 'div#DataTables_Table_0_length select'
LOCATOR_BUTTON_SEARCH = 'a#ctl00_MainContent_SearchButton'
LOCATOR_BUTTON_EXPORT = 'a#ctl00_MainContent_ExportButton'
LOCATOR_TABLE = 'table#DataTables_Table_0 tbody'
LOCATOR_RADIO_PUBLIC = 'input#ctl00_MainContent_chkSearchByPublic'


def download_data_private(page):

    # get a reference to the select menu that
    # allows you to switch years
    # https://playwright.dev/python/docs/api/class-page#page-locator
    select_year = page.locator(LOCATOR_SELECT_YEAR)

    # get a list of the options attached to this
    # select menu
    options = select_year.locator('option').all()

    # using a list comprehension with a conditional
    # `if` statement, get a list of values for these options,
    # but skip the option with "All" in the text
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    years = [x.get_attribute('value') for x in options if 'All' not in x.inner_text()]

    # loop over that list of values (years)
    # that we just isolated
    for year in years:

        # for each year, build a path to where
        # we want to download the file
        # using an f-string
        # https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals
        filename = f'{year}-private.zip'
        filepath = os.path.join(DIR_DATA, filename)

        # if file already exists, skip this one -- unless it's the current year
        if os.path.exists(filepath) and year != str(THIS_YEAR):
            continue

        # select the year from the select menu
        # https://playwright.dev/python/docs/api/class-locator#locator-select-option
        select_year.select_option(value=year)

        # set up the download
        # https://playwright.dev/python/docs/api/class-download
        with page.expect_download() as download_info:

            # click on the export button
            page.locator(LOCATOR_BUTTON_EXPORT).click()

            # wait for download to complete
            download = download_info.value

            # print a message letting us know what's happening
            print(f'Downloading {filepath}')

            # save the downloaded file to the path created above
            download.save_as(filepath)

        # make sure the page is done firing before
        # going to the next loop iteration
        page.wait_for_load_state('networkidle')

        # and throw in an explicit wait
        time.sleep(1)
    

def download_data_public(page):
    # a list of CSV headers for the public lobbyist files
    # making sure to match the same header names
    # from the private lobbyist files
    HEADERS_PUBLIC_CSV = [
        'YEAR',
        'LOBBYIST_LAST_NAME',
        'LOBBYIST_FIRST_NAME',
        'EMPLOYER'
    ]

    select = page.locator(LOCATOR_SELECT_YEAR)
    years = [x.inner_html() for x in select.locator('option').all() if 'All' not in x.inner_html()]  # noqa

    for year in years:

        filename = f'{year}-public.csv'
        filepath = os.path.join(DIR_DATA, filename)

        if os.path.exists(filepath) and year != str(THIS_YEAR):
            continue

        select = page.locator(LOCATOR_SELECT_YEAR)
        select.select_option(year)
        page.locator(LOCATOR_BUTTON_SEARCH).click()
        page.wait_for_load_state('networkidle')
       
        select_len = page.locator(LOCATOR_SELECT_TABLE_LEN)
        select_len.select_option("1000")

        table = page.locator(LOCATOR_TABLE)
        rows = table.locator('tr').all()

        with open(filepath, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=HEADERS_PUBLIC_CSV)
            writer.writeheader()

            for row in rows:
                cells = row.locator('td').all()
                year, name, dept = [x.inner_text() for x in cells]
                last, rest = [x.strip() for x in name.rsplit(',', 1)]
                data = [
                    year,
                    last,
                    rest,
                    dept
                ]

                writer.writerow(dict(zip(HEADERS_PUBLIC_CSV, data)))

        print(f'Wrote {filepath}')

        time.sleep(1)


def build_data_file():

    # get a list of downloaded files
    files_private = glob.glob(f'{DIR_DATA}/*.zip')
    files_public = glob.glob(f'{DIR_DATA}/*.csv')

    # start a list to hold individual data frames
    data_frames = []

    for file in files_private:
        df = pd.read_csv(
            file,
            compression='zip',
            delimiter='|'
        )

        data_frames.append(df)

    for file in files_public:
        df = pd.read_csv(file)
        data_frames.append(df)

    df = pd.concat(data_frames)

    df.sort_values(['YEAR', 'LOBBYIST_LAST_NAME', 'LOBBYIST_FIRST_NAME'], ascending=[False, True, True]).to_csv(CSV_FILEPATH, index=False)

    return CSV_FILEPATH


if __name__ == '__main__':

    if not os.path.exists(DIR_DATA):
        os.makedirs(DIR_DATA)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle')

        download_data_private(page)

        page.locator(LOCATOR_RADIO_PUBLIC).check()
        page.wait_for_load_state('networkidle')

        download_data_public(page)

    build_data_file()
