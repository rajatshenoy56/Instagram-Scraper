import scrapy
from selenium import webdriver
from time import sleep
import random
from urllib.parse import urlencode
import json

user_accounts = ['nike', 'adidas']


class InstagramSpider(scrapy.Spider):
    def __init__(self, name=None, **kwargs):
        super(InstagramSpider, self).__init__(name, **kwargs)
        # Change the path to the location of the chrome webdriver
        self.driver = webdriver.Chrome("C:\\Users\\hp\\Downloads\\chromedriver_win32\\chromedriver.exe")

    @staticmethod
    def get_selenium_login(driver, url):
        driver.maximize_window()
        driver.get(url)
        sleep(5)
        try:
            # Enter credentials of instagram account
            driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys("modman34")
            driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys("QneAzFTxg3%4ygN%")
            driver.find_element_by_xpath("//button[@type=\"submit\"]").click()
            sleep(10)
            # For the page after the login page
            driver.find_element_by_xpath("//button[text()='Not Now']").click()
            sleep(5)
        except:
            driver.quit()

    @staticmethod
    def get_selenium_response(driver, username):
        try:
            # returns the source code of the page
            driver.get("https://www.instagram.com/" + username)
            return driver.page_source.encode('utf-8')
        except:
            driver.quit()

    name = 'instagram'

    headers_list = [
        # Firefox 77 Mac
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        # Firefox 77 Windows
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        # Chrome 83 Mac
        {
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        },
        # Chrome 83 Windows
        {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
    ]

    def start_requests(self):
        # login to instagram
        self.get_selenium_login(self.driver, "https://www.instagram.com/")
        for username in user_accounts:
            print(username)
            headers = random.choice(self.headers_list)
            
            # The url doesnt really matter here as the source code of the page to be scraped is sent by selenium 
            url = f"https://www.instagram.com/{username}"
            
            # get the response page and send the response to be scraped
            response = self.get_selenium_response(self.driver, username)
            yield scrapy.Request(url, callback=self.parse, headers=headers, meta={'res': response})

    def parse(self, response):
        
        # Here response is overwritten by the actual source code of the page opened by selenium
        response = scrapy.Selector(text=response.meta['res'])
        
        x = response.xpath("//script[starts-with(.,'window._sharedData')]/text()").extract_first()

        json_string = x.strip().split('= ')[1][:-1]
        data = json.loads(json_string)

        user_id = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        next_page = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
                'has_next_page']
        edges = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_felix_video_timeline']['edges']

        for i in edges:
            # data extraction 
            url = 'https://www.instagram.com/p/' + i['node']['shortcode']
            video = i['node']['is_video']
            date_posted_timestamp = i['node']['taken_at_timestamp']
            like_count = i['node']['edge_liked_by']['count'] if "edge_liked_by" in i['node'].keys() else ''
            comment_count = i['node']['edge_media_to_comment']['count'] if 'edge_media_to_comment' in i[
                'node'].keys() else ''
            captions = ""
            if i['node']['edge_media_to_caption']:
                for i2 in i['node']['edge_media_to_caption']['edges']:
                    captions += i2['node']['text'] + "\n"

            if video:
                image_url = i['node']['display_url']
            else:
                image_url = i['node']['thumbnail_resources'][-1]['src']
                
            item = {'postURL': url, 'isVideo': video, 'timestamp': date_posted_timestamp, 'likeCount': like_count,
                    'commentCount': comment_count, 'image_url': image_url, 'captions': captions[:-1]}

            # For extracting video url
            if video:
                headers = random.choice(self.headers_list)
                yield scrapy.Request(url, callback=self.get_video, meta={'item': item}, headers=headers)
            else:
                item['videoURL'] = ''
                yield item

        # For the next page
        if next_page:
            headers = random.choice(self.headers_list)
            cursor = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
                    'end_cursor']

            # querying the graphql api for the next posts available
            di = {'id': user_id, 'first': 12, 'after': cursor}
            params = {'query_hash': 'e769aa130647d2354c40ea6a439bfc08', 'variables': json.dumps(di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)
            yield scrapy.Request(url, callback=self.parse_pages, meta={'pages_di': di}, headers=headers)

    def parse_pages(self, response):
        di = response.meta['pages_di']
        data = json.loads(response.text)
        for i in data['data']['user']['edge_owner_to_timeline_media']['edges']:
            # data extraction for all the next posts
            video = i['node']['is_video']
            url = 'https://www.instagram.com/p/' + i['node']['shortcode']
            if video:
                image_url = i['node']['display_url']
                video_url = i['node']['video_url']
            else:
                video_url = ''
                image_url = i['node']['thumbnail_resources'][-1]['src']

            date_posted_timestamp = i['node']['taken_at_timestamp']
            captions = ""
            if i['node']['edge_media_to_caption']:
                for i2 in i['node']['edge_media_to_caption']['edges']:
                    captions += i2['node']['text'] + "\n"

            comment_count = i['node']['edge_media_to_comment']['count'] if 'edge_media_to_comment' in i[
                'node'].keys() else ''

            like_count = i['node']['edge_liked_by']['count'] if "edge_liked_by" in i['node'].keys() else ''

            item = {'postURL': url, 'isVideo': video,
                    'timestamp': date_posted_timestamp, 'likeCount': like_count, 'commentCount': comment_count,
                    'image_url': image_url,
                    'videoURL': video_url, 'captions': captions[:-1]}
            yield item

        next_page = data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        if next_page:
            headers = random.choice(self.headers_list)
            cursor = data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            di['after'] = cursor
            # for the next available posts
            params = {'query_hash': 'e769aa130647d2354c40ea6a439bfc08', 'variables': json.dumps(di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)
            yield scrapy.Request(url, callback=self.parse_pages, meta={'pages_di': di}, headers=headers)

    def get_video(self, response):
        # Only for the first page as video url for all other pages are directly available
        item = response.meta['item']
        video_url = response.xpath('//meta[@property="og:video"]/@content').extract_first()
        item['videoURL'] = video_url

        yield item
