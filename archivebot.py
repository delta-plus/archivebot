import os
import sys
from optparse import OptionParser
import re
import datetime
import webbrowser
from webscraping import common, download, webkit, xpath
from selenium import webdriver
from socket import *

DELAY = 5 # delay between downloads
IMAGE_DIR = 'images' # directory to store screenshots
D = download.Download(delay=DELAY, num_retries=1)
driver = driver = webdriver.PhantomJS()
driver.set_window_size(1120, 550)

def historical_screenshots(website, days):
    """Download screenshots for website since archive.org started crawling

    website:
        the website to generate screenshots for
    days:
        the number of days difference between archived pages

    Returns a list of the downloaded screenshots
    """
    # the earliest archived time
    t0 = get_earliest_crawl(website)
    print 'Earliest version:', t0
    # the current time
    t1 = datetime.datetime.now()
    delta = datetime.timedelta(days=days)

    domain_folder = os.path.join(IMAGE_DIR, common.get_domain(website))
    if not os.path.exists(domain_folder):
        os.makedirs(domain_folder)

    screenshots = []
    while t0 <= t1:
        timestamp = t0.strftime('%Y%m%d')
        url = 'http://web-beta.archive.org/web/%s/%s/' % (timestamp, website)
        screenshot_filename = os.path.join(domain_folder, timestamp + '.jpg')
        boolean = True
        while boolean:
          try:
            driver.get(url)
            boolean = False
          except timeout:
            pass
        driver.save_screenshot(screenshot_filename)
        screenshots.append((url, t0, screenshot_filename))
        t0 += delta
    return screenshots


def get_earliest_crawl(website):
    # Return the datetime of the earliest crawl by archive.org for this website
    url = 'http://web-beta.archive.org/web/*/' + website
    boolean = True
    while boolean:
      try:
        driver.get(url)
        boolean = False
      except timeout:
        pass
    earliest_crawl = driver.find_element_by_xpath('.//*[@id=\'wbMetaCaptureDates\']/span/a[1]').text.replace(',', '')
    ts = datetime.datetime.strptime(earliest_crawl, '%B %d %Y')
    return ts


def show_screenshots(website, screenshots):
    # reverse the order so newest screenshots are first
    screenshots = screenshots[::-1]
    index_filename = os.path.join(IMAGE_DIR, common.get_domain(website), 'index.html')
    header = '\n'.join('<th><a href="%s">%s</a></th>' % (url, timestamp.strftime('%Y-%m-%d')) for url, timestamp, _ in screenshots)
    images = '\n'.join('<td style="vertical-align: top; padding: 10px"><a href="%(filename)s"><img style="width: 300px" src="%(filename)s" /></a></td>' % {'filename': os.path.basename(filename)} for url, timestamp, filename in screenshots)
    open(index_filename, 'w').write(
"""<html>
    <head>
        <title>{0}</title>
        <style>
        </style>
    </head>
    <body>
        <h1>History of <a href="{1}">{0}</a></h1>
        <table>
            <tr>
                {2}
            </tr>
            <tr>
                {3} 
            </tr>
        </table>
    </body>
</html>""".format(website, common.get_domain(website), header, images)
    )
    webbrowser.open(index_filename)
    

def main():
        if sys.argv[1]:
          if sys.argv[1] == 'years' or sys.argv[1] == 'y':
            days = 365
          elif sys.argv[1] == 'months' or sys.argv[1] == 'm':
            days = 30
          else:
            days = 1
        else:
          days = 1
        with open('sitelist.txt') as sites:
          for line in sites:
            url = line.strip()
            print 'Working on', url
            filenames = historical_screenshots(url, days)
            show_screenshots(url, filenames)


if __name__ == '__main__':
    main()
