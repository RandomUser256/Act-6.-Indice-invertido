from pathlib import Path

import scrapy

class CetysSpider(scrapy.Spider):
    name = "cetys"

    custom_settings = {
        'DEPTH_LIMIT': 100,
        'USER_AGENT' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    # Replace with the actual university domain
    allowed_domains = ['cetys.mx'] 
    start_urls = ['http://www.cetys.mx/']

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"cetys-{page}.html"
        Path(filename).write_bytes(response.body)

        # Menu bar links
        menu_link = response.css('.menu-wrap li a::attr(href)').get()
        
        if menu_link:
            absolute_url = response.urljoin(menu_link)
            yield scrapy.Request(url=absolute_url, callback=self.parse)

        # 2. (Optional) Recursively crawl other internal links if you want 
        # to explore deeper than just the primary menu bar
        '''
        for href in response.css('a::attr(href)').getall():
            absolute_url = response.urljoin(href)
            
            # Ensure links stay within the domain
            if urlparse(absolute_url).netloc in self.allowed_domains:
                yield scrapy.Request(url=absolute_url, callback=self.parse)
                '''
        # Yield data from the current page here
        yield {
            'url': response.url,
            'title': response.css('title::text').get()
        }