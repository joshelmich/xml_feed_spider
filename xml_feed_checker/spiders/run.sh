#!/bin/bash
rm -f xml_feed_spider.log
# run spider with feed on http://finlandned.org/websites.xml
scrapy runspider xml_feed_spider.py --logfile xml_feed_spider.log 
# process log to get necessary info
cat xml_feed_spider.log | grep xml_feed_spider | grep Status > status.txt 
# show info in a gui
#python gui.py






