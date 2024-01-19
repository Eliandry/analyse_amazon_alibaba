import csv

import scrapy
import time
import re


class AmazonReviewSpider(scrapy.Spider):
    name = "amazon_review"
    allowed_domains = ['amazon.ae']
    def __init__(self, *args,my_base_url='', **kwargs):
        super(AmazonReviewSpider, self).__init__(*args, **kwargs)
        self.my_base_url = my_base_url

        k = self.my_base_url.split(sep='/')
        name = k[3]
        id = k[5]
        self.start_urls=[
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=1',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=1',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=three_star&pageNumber=1',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=1',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=1',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_rvwer?ie=UTF8&reviewerType=avp_only_reviews&filterByStar=all_stars&pageNumber=1',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=avp_only_reviews&filterByStar=all_stars&pageNumber=1&sortBy=recent',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=avp_only_reviews&filterByStar=four_star&pageNumber=1&sortBy=recent',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_getr_d_paging_btm_next_2?ie=UTF8&reviewerType=avp_only_reviews&filterByStar=four_star&pageNumber=2&sortBy=recent&formatType=all_formats',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_getr_d_paging_btm_next_3?ie=UTF8&reviewerType=avp_only_reviews&filterByStar=four_star&pageNumber=3&sortBy=recent&formatType=all_formats',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_getr_d_paging_btm_next_3?filterByStar=critical&pageNumber=3',
        f'https://www.amazon.ae/{name}/product-reviews/{id}/ref=cm_cr_getr_d_paging_btm_prev_1?filterByStar=critical&pageNumber=1'
        ]
        self.filename = name + '.csv'  # Пример: 'product-reviews_B01LP0U5X0.csv'
        self.csvfile = open('media/'+self.filename, 'w', newline='', encoding='utf-8')
        self.csvwriter = csv.writer(self.csvfile)
        self.csvwriter.writerow(['star', 'comment'])  # Заголовки для CSV файла
    def parse(self, response):
        data = response.css('#cm_cr-review_list')

        star_rating = data.css('.review-rating')
        comments = data.css('.review-text')
        count = 0
        seen_comments = set()  # Сет для хранения уникальных комментариев
        for review in comments:
            time.sleep(1)  # Замедлять скрапинг не лучшая практика, лучше использовать DOWNLOAD_DELAY настройку
            d = ''.join(star_rating[count].xpath(".//text()").extract())
            star = "".join(c for c in d if c.isdecimal())[0]

            all_text = ''.join(review.xpath(".//text()").extract())
            text = re.sub(r'[^a-zA-Z0-9 ]', '', all_text)

            # Проверка на уникальность комментария перед его сохранением
            if text not in seen_comments:
                seen_comments.add(text)  # Добавление в сет для отслеживания уникальности
                self.csvwriter.writerow([star, text])
                yield {'star': star, 'comment': text}

            count += 1

    def close_spider(self, spider):
        self.csvfile.close()
# .xpath(".//text()").extract()
