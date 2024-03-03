import scrapy
import json
from mongoengine import connect
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('span small::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)


class AuthorsSpider(scrapy.Spider):
    name = "authors"
    start_urls = [
        'http://quotes.toscrape.com/',
    ]

    def parse(self, response):
        authors = {}
        for quote in response.css('div.quote'):
            author_name = quote.css('span small::text').get()
            if author_name not in authors:
                authors[author_name] = {
                    'fullname': author_name,
                    'born_date': quote.css('span.author-born-date::text').get(),
                    'born_location': quote.css('span.author-born-location::text').get(),
                    'description': response.css('div.author-description::text').get(),
                }

        with open('authors.json', 'w') as f:
            json.dump(list(authors.values()), f, indent=2)


if __name__ == "__main__":
    # Підключення до бази даних Atlas MongoDB
    connect("myFirstDatabase",
            host="mongodb+srv://osymashk:Langeron2024!@cluster0.oepyyjj.mongodb.net/",
            retryWrites=True,
            w="majority",
            appName="Cluster0")

    # Запуск краулера Scrapy
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'quotes.json'
    })
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()