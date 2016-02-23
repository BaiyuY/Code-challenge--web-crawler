import re
import sys
import threading
import httplib2
import string
import textwrap
import time
import shutil
from random import randint
from bs4 import BeautifulSoup

class Scraper:
    main_list = set() #list of fetched urls
    email_list = set()
    done_list = set()
    bots = None
    timeout = None
    domain = None
    lag = None
    depth = None
    should_die = False
    depth_counter = 0
    cycles = 0
    h = httplib2.Http()

    def __init__(self, domain=None,  bots=None, timeout=3, depth=3, lag=0.1):
        self.domain = domain
        self.main_list = [domain]
        self.bots = bots
        self.timeout = timeout
        self.depth = depth
        self.lag = lag
        self.h = httplib2.Http(".cache", self.timeout)
        self.h.follow_all_redirects = True
        self.h.follow_redirects = True

    def write_to_disk(self):
        # Only write to a file if email_list list is not empty
        if self.email_list:
            print "Writing emails..."
            file = open("emails.txt", "w")

            for email in self.email_list:
                file.write(email + "\n")
            file.close()



    def scrape_emails(self, webpage):
        # Find all emails in a webpage using a regex
        address =  sys.argv[1]
        email_list = re.findall(r"/^[-_a-z0-9\'+*$^&%=~!?{}]+(?:\.[-_a-z0-9\'+*$^&%=~!?{}]+)*" + re.escape(address) + r"$/iD", webpage)

        # Convert all of the found emails to lowercase
        email_list= [email.lower() for email in email_list]

        return set(email_list)


    def scrape_links(self, soup, domain):
        if domain.endswith("/"):
            domain = domain[0:-1]

        # For each link in the html code that has <a href= that is not blank (None) add it to url_list
        url_list = [link.get("href") for link in soup.findAll("a") if link.get("href") is not None]

        # First type of non-absolute links
        nonAbsolute1 = [link[1:] for link in url_list if link.startswith("/")]
        nonAbsolute1 = [domain + "/" + link for link in nonAbsolute1]

        # Second type of non-absolute links
        nonAbsolute2 = [domain + "/" + link for link in url_list if not link.startswith("http") and not link.startswith("/") and not link.startswith(".")]

        url_list.extend(nonAbsolute1)
        url_list.extend(nonAbsolute2)

        # Only scrape first party domain
        url_list = [url for url in url_list if url.startswith(domain)]

        # Remove all links that do not start with "http"
        url_list = [url for url in url_list if url.startswith("http")]

        # For non threading
        return url_list

    def sub_request(self, element):
        method = "GET"
        headers = {"User-Agent": self.bots[randint(0, len(self.bots) - 1)]}
        body = None

        return self.h.request(element, method, body, headers, redirections=15)

    def scrape(self):
        # Keep scraping links as long as there are links in self.main_list
        while self.main_list:
            try:
                # Set lag between connection attempts
                time.sleep(self.lag)

                # Grab emails and links from next url
                new_url_list, new_email_list = self.scrape_url(self.main_list.pop(0))

                self.update_list(new_url_list, new_email_list)
                self.cycles += 1

                # Write to disk
                if self.cycles % 100 == 0:
                    if self.email_list:
                        self.write_to_disk()

            except (KeyboardInterrupt, SystemExit):
                print "\n\nKeyboardInterrupt caught, exiting..."
                self.write_to_disk()
                shutil.rmtree(".cache")
                self.should_die = True
                sys.exit(0)
        try:
            self.write_to_disk()
        except:
            print "Unable to initially scrape the target; double-check domain name."


    def update_list(self, new_url_list, new_email_list):
        """
        update email_list, done_list, main_list and cycle
        """
        self.email_list.union(new_email_list)
        for url in new_url_list:
            if not url in done_list:
                self.main_list.add(url)
        self.done_list.add(url)


    def scrape_url(self, url):
        # Dynamically determine depth
        stripurl = string.replace(url, self.domain, '')
        self.depth_counter = string.count(stripurl[:-1], '/') + 1

        # Open the remote connection
        content = ""
        try:
            resp, content = self.sub_request(url)
            soup = BeautifulSoup(content)
            # Grab all of the links from url and add them to main_list while abiding by depth
            if self.depth_counter < self.depth:
                url_list = self.scrape_links(soup, url)
                email_list = self.scrape_emails(content)
                return url_list, email_list

        except:
            print "Error has occured in crawling " + url
            return None


