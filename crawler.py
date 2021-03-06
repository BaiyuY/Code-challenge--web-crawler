from Scraper import *
import sys
import shutil
import os 
import time
import threading



domain = None
crawler = None
timeout = 5
depth = 10
lag = 0.1
bots = ["Googlebot/2.1 (+http://www.google.com/bot.html)", "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)", "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"]
bot = bots[1]
emailscan = False
tprint = None

# Initializes everything
def init():
	global crawler
	global domain
	global bot
	global timeout
	global lag
	global depth
	global emailscan
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
	cmdArgs()
	
	# Initialize scraper object
	crawler = Scraper(domain, bot, timeout, lag, depth, emailscan)

	# Pretty print thread
	tprint = threading.Thread(target=ThreadPrettyPrint)
	
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
	crawler.shouldDie = True

# Command line args
def cmdArgs():
	global domain
	global bot
	global timeout
	global lag
	global depth
	global emailscan
	
	

	# Recover full domain
	domain = "http://" + sys.argv[1]

	# Add "/" to end of domain
	if not sys.argv[1].endswith("/"):
		domain = domain + "/"



def ThreadPrettyPrint():
	global crawler
	

	print "User-agent: " + crawler.bot
	print "Depth: " + str(crawler.depth)
	print "Lag: " + str(crawler.lag)
	print "Timeout: " + str(crawler.timeout)
	
	while crawler.shouldDie != True:
		print "Cycles: " + str(crawler.cycles)
		print "Remaining Links: " + str(len(crawler.mainList))
		print "Scanned links: " + str(len(crawler.doneList))
		
		if crawler.emailscan == True:
			print "Found these email addresses: " + str(len(crawler.emailList)) # Only print email list when it is not empty
		
		print
		time.sleep(1)


init()
start()
stop()
