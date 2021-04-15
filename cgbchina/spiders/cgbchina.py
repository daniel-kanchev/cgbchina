import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cgbchina.items import Article


class cgbchinaSpider(scrapy.Spider):
    name = 'cgbchina'
    start_urls = ['http://www.cgbchina.com.cn/Channel/13260778?_tp_t4356=1']
    page = 1

    def parse(self, response):
        articles = response.xpath('//ul[@class="newList"]//li')
        if articles:
            for article in articles:

                link = article.xpath('./a/@href').get()
                date = article.xpath('./span/text()').get()
                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

            self.page += 1

            next_page = f'http://www.cgbchina.com.cn/Channel/13260778?_tp_t4356={self.page}'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2//text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="textContent"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
