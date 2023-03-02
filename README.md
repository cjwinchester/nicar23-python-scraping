# NICAR 2023: Web scraping with Python

### 🔗 [bit.ly/nicar23-scraping](https://bit.ly/nicar23-scraping)

This repo contains materials for a half-day workshop at the NICAR 2023 data journalism conference in Nashville on using Python to scrape data from websites.

The session is scheduled for Sunday, March 5, from 9 a.m. - 12:30 p.m. in room `Midtown 3` on Meeting Space Level 2.

### First step

Open the Terminal application. Copy and paste this text into the Terminal and hit enter:

```bash
cd ~/Desktop/hands_on_classes/20230305-sunday-web-scraping-with-python--preregistered-attendees-only && source env/bin/activate
```

### Course outline
- Do you really need to scrape this?
- Process overview:
    - Fetch, parse, write data to file
    - Some best practices
        - Make sure you feel OK about whether your scraping project is (legally, ethically, etc.) allowable
        - Don't DDOS your target server
        - When feasible, save copies of pages locally, then scrape from those files
        - [Rotate user-agent strings](https://www.useragents.me/) and other headers if necessary to avoid bot detection
- Using your favorite brower's inspection tools to deconstruct the target page(s)
    - See if the data is delivered to the page in a ready-to-use format, such as JSON ([example](https://sdlegislature.gov/Session/Archived))
    - Is the HTML part of the actual page structure, or is it built on the fly when the page loads? ([example](https://rrctx.force.com/s/complaints))
    - Can you open the URL directly in an incognito window and get to the same content, or does the page require a specific state to deliver the content (via search navigation, etc.)? ([example](https://rrctx.force.com/s/ietrs-complaint/a0ct0000000mOmhAAE/complaint0000000008))
    - Are there [URL query parameters](https://en.wikipedia.org/wiki/Query_string) that you can tweak to get different results? ([example](https://www.worksafe.qld.gov.au/news-and-events/alerts))
- Choose tools that the most sense for your target page(s) -- a few popular options:
    - [`requests`](https://requests.readthedocs.io/en/latest/) and [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
    - [`playwright`](https://playwright.dev/python) (optionally using `BeautifulSoup` for the HTML parsing)
    - [`scrapy`](https://scrapy.org/) for larger spidering/crawling tasks
- Overview of our Python setup today
    - Activating the virtual environment
    - Jupyter notebooks
    - Running `.py` files from the command line
- Our projects today:
    - [Maryland WARN notices](md-warn-notices)
    - [U.S. Senate press gallery](us-senate-press-gallery)
    - [IRE board members](ire-board)
    - [South Dakota lobbyist registration data](sd-lobbyists)
    - [Texas Railroad Commission complaints](tx-railroad-commission)

### Additional resources
- Need to scrape on a timer? [Try GitHub Actions](https://palewi.re/docs/first-github-scraper) (Other options: Using your computer's scheduler tools, putting your script on a remote server with a [`crontab` configuration](https://en.wikipedia.org/wiki/Cron), [switching to Google Apps Script and setting up time-based triggers](https://developers.google.com/apps-script/guides/triggers), etc.)
- [A neat technique for copying data to your clipboard while scraping a Flourish visualization](https://til.simonwillison.net/shot-scraper/scraping-flourish)
- [Walkthrough: Class-based scraping](https://blog.apps.npr.org/2016/06/17/scraping-tips.html)


### Running this code at home
- Install Python, if you haven't already ([here's our guide](https://docs.google.com/document/d/1cYmpfZEZ8r-09Q6Go917cKVcQk_d0P61gm0q8DAdIdg/edit))
- Clone or download this repo
- `cd` into the repo directory and install the requirements, preferably into a virtual environment using your tooling of choice: `pip install -r requirements.txt`
- `playwright install`
- `jupyter notebook` to launch the notebook server
