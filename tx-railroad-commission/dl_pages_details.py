import os
import glob
import time

from dl_pages_results import DIR_PAGES_RESULTS, BASE_URL

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, expect


# make a reference to the directory where
# the downloaded detail pages will land
DIR_PAGES_DETAIL = 'pages-detail'


def get_detail_page_links():
    '''
    A function to extract the detail page links
    from the results HTML files that we downloaded separately
    '''

    # an empty list to hold the extracted links
    detail_page_links = []

    # use the glob module to nab a list of all
    # the HTML files we want to parse
    # https://docs.python.org/3/library/glob.html
    filepaths_results = sorted(glob.glob(f'{DIR_PAGES_RESULTS}/*.html'))

    # loop over each results file
    for results_file in filepaths_results:

        # open it and read the HTML
        with open(results_file, 'r') as infile:
            html = infile.read()

        # turn it into soup
        soup = BeautifulSoup(html, 'html.parser')

        # find the table rows
        rows = soup.tbody.find_all('tr')

        # use a list comprehension to grab the links from each row
        # and prepend the base URL to ensure a fully
        # qualified URL to save a step later
        # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        links = [f"{BASE_URL}/s{x.find('a')['href']}" for x in rows]

        # add these links to the main list
        detail_page_links.extend(links)

    # return the list of links we just populated
    return detail_page_links


def dl_pages_detail():

    # call the function to get the links and store the results
    links = get_detail_page_links()

    # set up the playwright object
    # https://playwright.dev/python/docs/library#usage
    with sync_playwright() as p:

        # create a new Chromium browser, which
        # operates in headless mode by default
        browser = p.chromium.launch()

        # open a new page
        page = browser.new_page()

        # loop over the links we just grabbed
        for link in links:

            # use the unique ID in the URL as the filename
            filename = f"{link.split('/')[-1]}.html"

            # build the file path
            filepath = os.path.join(
                DIR_PAGES_DETAIL,
                filename
            )

            # check to see if we already downloaded the page
            if not os.path.exists(filepath):

                # if not, navigate to the page
                # and wait for the assets to load
                page.goto(
                    link,
                    wait_until='networkidle'
                )

                expect(
                    page.get_by_title('Inspection Packages')
                ).to_be_visible()

                expect(
                    page.get_by_text('Complaint Name')
                ).to_be_visible()

                time.sleep(2)


                if 'RRC SIGN IN' in page.locator('body').inner_text().upper():
                    print(f'    PROBLEM downloading {link}')
                    continue

                # target the content div and grab the HTML
                content = page.locator('html').inner_html()  # noqa

                # if not, download it
                with open(filepath, 'w') as outfile:
                    outfile.write(content)

                # and let us know what's up
                print(f'Downloaded {filepath}')

                # wait a tick before moving on to the next page
                time.sleep(0.5)

        # close the browser
        browser.close()


if __name__ == '__main__':
    dl_pages_detail()
