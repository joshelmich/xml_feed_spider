import scrapy

class site_item(scrapy.Item):
    url = scrapy.Field()
    username = scrapy.Field()
    password = scrapy.Field()
    x_path = scrapy.Field()
    content_requirement = scrapy.Field()
