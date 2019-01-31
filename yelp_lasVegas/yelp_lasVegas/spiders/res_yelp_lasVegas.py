# -*- coding: utf-8 -*-
import scrapy


class ResYelpLasvegasSpider(scrapy.Spider):
    name = 'res_yelp_lasVegas'
    allowed_domains = ['yelp.com']
    start_urls = ['https://www.yelp.com/search?find_desc=Restaurants&find_loc=Las%20Vegas']

    def parse(self, response):
        listings = response.xpath('//div[@class = "lemon--div__373c0__1mboc businessName__373c0__1fTgn border-color--default__373c0__2oFDT"]')
        for listing in listings:
            tmp = listing.xpath('.//a/@href').extract_first()
            if tmp is not None and '/biz/' in tmp:
                link = tmp
                text = listing.xpath('.//a/text()').extract_first()

                yield scrapy.Request(response.urljoin(link), callback=self.parse_listing, meta = {'text': text, 'link': link})


        next_page_url = response.xpath('//*[@class="lemon--a__373c0__IEZFH link__373c0__29943 next-link navigation-button__373c0__1D3Ug link-color--blue-dark__373c0__1mhJo link-size--default__373c0__1skgq"]/@href').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url), callback = self.parse)



    def parse_listing(self, response):
        text = response.meta['text']
        link = response.meta['link']


        price_symbol = response.xpath('//span[@class = "business-attribute price-range"]/text()').extract_first()
        price = response.xpath('//*[@class="nowrap price-description"]/text()').extract_first().strip()

        tmp_claimed = response.xpath('//*[@class = "u-nowrap claim-status_teaser js-claim-status-hover"]/text()').extract()[1].strip()
        if tmp_claimed == 'Claimed':
            claimed = 1
        else:
            claimed = 0

        attributes_names = response.xpath('//*[@class = "short-def-list"]/dl/dt/text()').extract()
        attributes_options = response.xpath('//*[@class = "short-def-list"]/dl/dd/text()').extract()
        attr_keys = map(str.strip, attributes_names)
        attr_values = map(str.strip, attributes_options)
        attributes = dict(zip(attr_keys, attr_values))

        openday_names = response.xpath('//table[@class = "table table-simple hours-table"]//th[1]//text()').extract()
        openday_h1 = response.xpath('//table[@class = "table table-simple hours-table"]//td[1]/span[1]//text()').extract()
        openday_h2 = response.xpath('//table[@class = "table table-simple hours-table"]//td[1]/span[2]//text()').extract()
        open_hours = [m+'-'+n for m,n in zip(openday_h1, openday_h2)]

        opentime = dict(zip(openday_names, open_hours))


        yield {'text': text, 'price symbol': price_symbol, 'price': price, 'claimed': claimed, 'attributes': attributes, 'opentime':opentime}
        #yield {'text': text, 'price symbol': price_symbol, 'price': price, 'claimed': claimed, 'attributes': attributes}

