import os
import time

from playwright.sync_api import sync_playwright


# create a variable pointing to the directory where
# the cached pages should land
DIR_PAGES_RESULTS = 'pages-results'

# create a variable pointing to the base URL, which
# we'll use in a couple places
BASE_URL = 'https://rrctx.force.com'


def download_pages_results():

    # check to see if this directory exists
    if not os.path.exists(DIR_PAGES_RESULTS):

        # if not, create it
        os.makedirs(DIR_PAGES_RESULTS)

    # set up the playwright object
    # https://playwright.dev/python/docs/library#usage
    with sync_playwright() as p:

        # create a new Chromium browser, which
        # operates in headless mode by default
        browser = p.chromium.launch()

        # open a new page
        page = browser.new_page()

        # go to the initial complaints results page
        # and wait until all the assets are loaded
        # using an f-string to build the URL to navigate to
        # https://docs.python.org/3/tutorial/inputoutput.html#tut-f-strings
        page.goto(
            f'{BASE_URL}/s/complaints',
            wait_until='networkidle'
        )

        # find the table and grab the HTML
        table = page.locator('table').inner_html()

        # get the page number we're on (1)
        # by finding the pagination element at the bottom of the page
        page_tracker = page.get_by_text(' | Page ').inner_text()

        # ... and then parsing out the page number with some splits
        page_num = page_tracker.split('Page')[1].split('of')[0].strip()

        # set up the filename -- using the .zfill()
        # string method to pad out the number
        # to three digits -- and the file path
        filename = f'{page_num.zfill(3)}.html'
        filepath = os.path.join(
            DIR_PAGES_RESULTS,
            filename
        )

        # open the file and write
        # the table HTML captured above
        with open(filepath, 'w') as outfile:
            outfile.write(table)

        # let us know what's up
        print(f'Downloaded {filepath}')
        
        # next, create a process to iterate through
        # the other pages of the search results --
        # a better move here would be to write a 
        # recursive function, but a hacky while True / break
        # statement works too

        while True:
            # find the "Next" button
            next_button = page.locator('button', has_text='Next')

            # click it
            next_button.click()

            # wait for the next page to load
            page.wait_for_load_state('networkidle')

            # find the table and grab the HTML
            table = page.locator('table').inner_html()

            # get the page number we're on
            # by finding the pagination element at the bottom of the page
            page_tracker = page.get_by_text(' | Page ').inner_text()

            # and then parsing out the page number with some splits
            page_num = page_tracker.split('Page')[1].split('of')[0].strip()

            # set up the filename and path
            filename = f'{page_num.zfill(3)}.html'

            filepath = os.path.join(
                DIR_PAGES_RESULTS,
                filename
            )

            # open the file and write into
            # it the table HTML captured above
            with open(filepath, 'w') as outfile:
                outfile.write(table)

            # let us know what's up
            print(f'Downloaded {filepath}')

            # see if this is the last page
            lpage = int(page_tracker.split('of')[-1])

            # if the {x} in "Page {x} of {y}" number
            # is the same as {y}, we're done
            if int(page_num) == lpage:
                break

            # if not the last page,
            # wait half a second before moving on to the next page
            time.sleep(0.5)

        # shut down the browser
        browser.close()


if __name__ == '__main__':
    download_pages_results()
