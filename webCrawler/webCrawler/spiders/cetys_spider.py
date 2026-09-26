from fileinput import filename
from pathlib import Path

import scrapy

class CetysSpider(scrapy.Spider):
    name = "cetys"
    allowed_domains = ["cetys.mx"]
    start_urls = ["https://www.cetys.mx/"]

    def parse(self, response):
        # 1. Extract all href attributes within the main <header id="header"> tag
        header_links = response.css("header#header a::attr(href)").getall()

        # 2. Filter out anchor links ('#'), empty links, and javascript actions
        valid_links = set()
        for link in header_links:
            clean_link = link.strip()
            if (
                clean_link
                and not clean_link.startswith("#")
                and not clean_link.startswith("javascript:")
            ):
                # Convert relative URLs to absolute URLs
                absolute_url = response.urljoin(clean_link)
                valid_links.add(absolute_url)

        num_pages = 0

        # 3. Iterate through links and yield requests to explore them
        for idx, url in enumerate(sorted(valid_links), start=1):
            if (num_pages >= 100):
                break
            page_id = f"page-{idx:03d}"
            yield response.follow(url, callback=self.parse_header_page, 
                cb_kwargs={
                    "page_id": page_id,
                }
            )
            num_pages = num_pages + 1

    def parse_header_page(self, response, page_id):
        # Process the crawled header pages here
        self.logger.info(f"Crawled header page: {response.url}")

        pageName = response.css('title::text').get()
        filename = f'{page_id}.html'


        Path(filename).write_bytes(response.body)

        yield {
            "id": page_id,
            "url": response.url,
            "title": response.css("title::text").get("").strip(),
            "meta_description": response.css(
                'meta[name="description"]::attr(content)'
            ).get(""),
            "http_status": response.status,
        }