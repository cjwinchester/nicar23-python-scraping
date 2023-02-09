from dl_pages_results import download_pages_results
from dl_pages_details import dl_pages_detail
from scrape_detail_pages import scrape_data

if __name__ == '__main__':
    print('Downloading results pages ...')
    download_pages_results()
    print()

    print('Downloading detail pages ...')
    dl_pages_detail()
    print()

    print('Scraping data ...')
    file_details = scrape_data()
    print()

    print(f'Done! Wrote {file_details["record_count"]:,} records to {file_details["filepath"]}')
