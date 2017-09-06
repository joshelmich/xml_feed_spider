this software is made for Ubuntu 17.04 using python 2.7 and PyQt4

check: python ..version

Install:

sudo apt-get update
sudo apt-get install python2.7 
sudo apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
sudo apt-get install python-qt4

pip install scrapy
pip install lxml

Optional (needed for hashing passwords): 

pip install cryptography

Not recommended, but works

sudo apt-get install python-scrapy

OTHER PREREQUISITES

mkdir scrapy
cd scrapy
scrapy startproject xml_feed_checker xml_feed_check

startproject is necessary to create some configs in scrapy folders
without this command the DownloadTimer implemented in middlewares.py and configured settings.py will not be called

move the code that you cloned from github (git clone https://github.com/joshelmich/xml_feed_spider.git) to the folders created by the scrapy startproject command. You can overwrite everything.

the file run.sh executes the spider xml_feed_spider.py
this spider: 

1) reads http://finlandned.org/websites.xml (sample provided)
2) checks the websites and requirements defined in there
3) generates a log

after the spider is finished. The log file get processed to catch the relevant logs. The result is stored in status.txt

you can view the result of run.sh by typing 

cat status.txt

USING THE GUI

if you type

python gui.py

on the command line

run.sh gets executed and a window with necessary information pops up. 
The gui.py refreshes the info on a regular basis by executing run.sh and parsing the contents of status.txt


