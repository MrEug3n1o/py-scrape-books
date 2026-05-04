import scrapy
from scrapy.http import Response
import re

from scrape_books.scrape_books.items import ScrapeBooksItem

rating_dict = {
            "Zero": 0,
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_book(self, response: Response, **kwargs):
        item = ScrapeBooksItem()

        item["title"] = response.css("h1::text").get()
        item["price"] = response.css(".price_color::text").get()
        instock = response.css(".instock.availability::text").get()
        instock = re.search(r"(\d+)", instock)
        item["amount_in_stock"] = instock
        rating = response.css(".star-rating::attr(class)").get()
        rating = rating.split()[-1]
        item["rating"] = rating_dict.get(rating)
        item["category"] = response.css("ul.breadcrum li:nth-last-child(2)::text").get()
        item["description"] = response.xpath(
            "//div[@id='product_describtion']/following-sibling::p/text()"
        ).get()
        item["upc"] = response.css("table tr:first-child td:first-child::text").get()

        yield item