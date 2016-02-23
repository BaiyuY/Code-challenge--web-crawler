from Scraper import *
import sys
import shutil
import os
import time
import threading

domain = None
crawler = None
timeout = 5
depth = 3
lag = 0.1
bots = ["Googlebot/2.1 (+http://www.google.com/bot.html)", "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)", "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"]
tprint = None

# Initializes everything
def init():
    global crawler
    global domain
    global bot
    global timeout
    global lag
    global depth
    global tprint

    # Remove previous files
    try:
        shutil.rmtree(".cache")
    except OSError:
        pass

    try:
        os.remove("emails.txt")
    except OSError:
        pass

    # Process cmd line arguments
    cmd_args()

    # Initialize scraper object
    crawler = Scraper(domain, bot, timeout, lag, depth)

    # Pretty print thread
    tprint = threading.Thread(target=thread_pretty_print)


# Starts scraping
def start():
    global crawler
    global tprint

    tprint.start()
    crawler.Scrape()


# Called when the application is going to end
def stop():
    global crawler
    # Remove .cache if it exists
    shutil.rmtree(".cache")
    crawler.should_die = True


# Command line args
def cmd_args():
    global domain
    global bot
    global timeout
    global lag
    global depth

    # Recover full domain
    domain = "http://" + sys.argv[1]

    # Add "/" to end of domain
    if not sys.argv[1].endswith("/"):
        domain = domain + "/"


def thread_pretty_print():
    global crawler

    print "User-agent: " + crawler.bot
    print "Depth: " + str(crawler.depth)
    print "Lag: " + str(crawler.lag)
    print "Timeout: " + str(crawler.timeout)

    while crawler.should_die != True:
        print "Cycles: " + str(crawler.cycles)
        print "Remaining Links: " + str(len(crawler.main_list))
        print "Scanned links: " + str(len(crawler.done_list))

        print "Found these email addresses: " + str(len(crawler.email_list)) # Only print email list when it is not empty

        print
        time.sleep(1)


init()
start()
stop()
