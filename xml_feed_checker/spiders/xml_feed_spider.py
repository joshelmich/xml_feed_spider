# Author Jos Helmich
# email: jos.helmich@finlandned.org

import scrapy
from scrapy.spiders import XMLFeedSpider
from scrapy.utils.log import configure_logging
from scrapy.utils.spider import iterate_spider_output
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from items import site_item
import logging

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from time import time
from scrapy.http import Response

class MySpider(XMLFeedSpider):
	name = 'xml_feed_spider'
	
	custom_settings = {
		'LOG_FILE': "xml_feed_spider.log"
	}
	my_items = []
	#allowed_domains = ['finlandned.org']
	start_urls = ["http://finlandned.org/websites.xml"]
	print start_urls
	iterator = 'iternodes' # This is actually unnecesary, since it's the default value
	itertag = 'site'
	configure_logging(install_root_handler=False)
	logger = logging.getLogger('xml_feed_spider.log')
	logger.info('its started')
	
# reads a website node from XML file	
	def parse_node(self, response, node):		
		an_item = site_item()
		feed_items = ItemLoader(item=an_item, response=response)		
		url = node.xpath('url').extract()		
		print "url", url
		an_item['url'] = url
		an_item['username'] = node.xpath('username').extract()
		an_item['password'] = node.xpath('password').extract()
		an_item['x_path'] = node.xpath('x_path').extract()
		an_item['content_requirement'] = node.xpath('content_requirement').extract()
		self.my_items.append(an_item)
		return feed_items.item  
	
# sometimes a string is returned with tag included, we are only interested in the content of the node	
	def strip_tag(self, a_string, tagname):
		empty_tag = "<" + tagname + "/>"
		if empty_tag == a_string:
			return ""
		begin_tag = "<" + tagname + ">"
		end_tag = "</" + tagname + ">"		
		temp_strings = a_string.split(begin_tag)
		temp_strings = temp_strings[1].split(end_tag)
		temp_string = temp_strings[0]
		return temp_string
		
# sometimes a string is returned with CDATA included, we are only interested in the content of the node			
	def strip_cdata(self, a_string):
		if a_string.find("![CDATA[") == -1:
			return a_string
		temp_string = a_string.split("![CDATA[")
		temp_string = temp_string[1].split("]]")
		return temp_string[0]

# executes when a link test does not result in an error
# in that case we test for a required xpath
# when a required xpath is found we test for specific required content
# download time is taking from middleware object DownloadTimer  
	def parse_web_url_response(self, response):
		if response.status == 200:
			print "response.url", response.url.encode("utf8")
			download_time = response.meta['__end_time'] - response.meta['__start_time']
			i = 0
			for i in range(0, len(self.my_items)):				
				temp_string = self.my_items[i]['url'][0]
				temp_string = self.strip_tag(temp_string, 'url')
				if temp_string == response.url:
					temp_x_path = self.my_items[i]['x_path'][0]
					x_path = self.strip_tag(temp_x_path, 'x_path')
					temp_req_content = self.my_items[i]['content_requirement'][0]					
					req_content = self.strip_tag(temp_req_content, 'content_requirement')					
					if x_path != "![CDATA[None]]" and x_path!="":
						temp_content = Selector(text=response.body).xpath(x_path).extract()
						if temp_content == []:
							content = ""
						else:
							content = temp_content[0]
						req_content = self.strip_cdata(req_content)
						if req_content == "":
							if content == "":
								self.logger.error("Status; RequiredPathNotFound on %s , DownloadTime: %.3f", response.url, download_time)
							else:
								self.logger.info("Status; NoError on %s , DownloadTime: %.3f", response.url, download_time)							
						elif content != req_content:
							self.logger.error("Status; RequiredContentNotFound on %s , DownloadTime: %.3f", response.url, download_time)
						else:
							self.logger.info("Status; NoError on %s , DownloadTime: %.3f", response.url, download_time)
						
					else:
						self.logger.info("Status; NoError on %s , DownloadTime: %.3f", response.url, download_time)
					break
		return
		
# if a link test results in failure we try to find the specific error
# download time is taking from middleware object DownloadTimer 		
	def parse_request_error(self, failure):
		response = failure.value.response
		download_time = response.meta['__end_time'] - response.meta['__start_time']
		if failure.check(HttpError):
			# these exceptions come from HttpError spider middleware
			# you can get the non-200 response
			response = failure.value.response
			self.logger.error('Status; HttpError on %s , DownloadTime: %.3f', response.url, download_time)
		elif failure.check(DNSLookupError):
			# this is the original request
			request = failure.request
			self.logger.error('Status; DNSLookupError on %s , DownloadTime: %.3f', request.url, download_time)
		elif failure.check(TimeoutError, TCPTimedOutError):
			request = failure.request
			self.logger.error('Status; TimeoutError on %s , DownloadTime: %.3f', request.url, download_time)		

# parses the nodes found in XML file		
	def parse_nodes(self, response, nodes):
		response.selector.remove_namespaces()
		for selector in nodes:
			ret = iterate_spider_output(self.parse_node(response, selector))		
			for result_item in self.process_results(response, ret):
				temp_url = result_item['url'][0].split('<url>')
				temp_url = temp_url[1].split('</url>')
				web_url = temp_url[0]
				yield scrapy.Request(url=web_url, 
					callback=self.parse_web_url_response, 
					errback=self.parse_request_error, 
					dont_filter=True)
