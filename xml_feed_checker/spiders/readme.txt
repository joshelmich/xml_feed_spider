this software is made for Ubuntu 17.04 using python 2.7 and PyQt4

check: python ..version

Install:

sudo apt-get update
sudo apt-get install python2.7 
sudo apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
sudo apt-get install python-qt4

pip install Scrapy
pip install lxml

if needed for hashing passwords 

pip install cryptography

Not recommended, but works

sudo apt-get install python-scrapy

You can edit the files using your favourite editor

mkdir scrapy
cd scrapy
scrapy startproject xml_feed_checker xml_feed_check

startproject is necessary to create some configs in scrapy folders
scrapy genspider -t xmlfeed xml_feed_spider http://www.finlandned.org

