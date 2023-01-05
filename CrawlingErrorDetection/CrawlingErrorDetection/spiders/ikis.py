# -*- coding: utf-8 -*
import os
import gridfs
import pymongo
import jpype
import scrapy
import re
import requests
from bs4 import BeautifulSoup
from CrawlingErrorDetection.items import CrawlingErrorDetectionItem
from tika import parser
from tempfile import NamedTemporaryFile
from itertools import chain

control_chars = ''.join(map(chr, chain(range(0, 9), range(11, 32), range(127, 160))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(control_chars))

import configparser

config = configparser.ConfigParser()
config.read('./../lib/config.cnf')

import time

def print_time():
    tm = time.localtime(time.time())
    string = time.strftime('%Y-%m-%d %I:%M:%S %p', tm)
    return string


class IkisSpider(scrapy.Spider):
    name = 'ikis'
    allowed_domains = ['http://www.ikistongil.org/']
    start_urls = ['http://www.ikistongil.org/data/data.php?ptype=&page=1&code=inner']

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.start_urls = 'http://www.ikistongil.org/data/data.php?ptype=&page=1&code=inner'
        # 몽고에 넣겠다
        self.client = pymongo.MongoClient(config['DB']['MONGO_URI'])
        self.db = self.client['attchment']
        self.fs = gridfs.GridFS(self.db)
        # jpype, java lib 연결
        jarpath = os.path.join(os.path.abspath('.'), './../lib/hwp-crawl.jar')
        jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % jarpath)

    def start_requests(self):
        yield scrapy.Request(self.start_urls, self.parse, dont_filter=True)

    def parse(self, response):
        page_no = 1
        last_page_no = 3
        while True:
            if page_no > last_page_no:
                break
            link = 'http://www.ikistongil.org/data/data.php?ptype=&page=' + str(page_no) + '&code=inner'
            yield scrapy.Request(link, callback=self.parse_each_pages,
                                 meta={'page_no': page_no, 'last_page_no': last_page_no, 'link': link},
                                 dont_filter=True)

            page_no += 1

    def parse_each_pages(self, response):
        link = response.meta['link']

        htmls = requests.get(link)
        bs = BeautifulSoup(htmls.content, 'html.parser')

        for url_oj in bs.find_all("td", align="left"):
            url_href = url_oj.find('a')
            url_href = str(url_href)
            url_href = url_href.split('">')[0]
            url_href = url_href.replace("&amp;", "&")
            url_href = url_href.replace('<a href="', '')

            url = "http://www.ikistongil.org" + url_href
            print("url", url)
            yield scrapy.Request(url, callback=self.parse_post, dont_filter=True, meta={'url': url})

    def parse_post(self, response):
        item = CrawlingErrorDetectionItem()
        original_url = response.meta['url']

        htmls = requests.get(original_url)
        bs = BeautifulSoup(htmls.content, 'html.parser')

        title = bs.find("td", width="80%").get_text()

        date = bs.find("td", width="35%").get_text()
        print("date:", date)

        writer = bs.find("td", align="left").get_text()
        print("writer:", writer)

        body = bs.find("div", "board_in").get_text().strip()
        print("body:", body)
        top_category = "IKIS 자료실"

        item[config['VARS']['VAR1']] = title.strip()
        item[config['VARS']['VAR4']] = date.strip()
        item[config['VARS']['VAR3']] = writer.strip()
        if body:
            item[config['VARS']['VAR2']] = body.strip()
        item[config['VARS']['VAR5']] = "남북사회통합연구원"
        item[config['VARS']['VAR6']] = "http://www.ikistongil.org/"
        item[config['VARS']['VAR7']] = top_category
        item[config['VARS']['VAR8']] = original_url

        file_name = bs.find("td", colspan="3", align="left").find('a')

        if str(type(file_name)) == "<class 'NoneType'>":
            print("###############object type is NoneType!#################")
            file_name = None
        else:
            file_name = file_name.get_text()
        print("file_name:", file_name)

        if file_name:
            file_href = bs.find("td", colspan="3", align="left").find('a')["href"]
            file_href = str(file_href)
            file_download_url = 'http://www.ikistongil.org' + file_href
            print("file_download_url:", file_download_url)

            item[config['VARS']['VAR10']] = file_download_url
            item[config['VARS']['VAR9']] = file_name

            if file_name.find("hwp") != -1:
                print('find hwp')
                yield scrapy.Request(file_download_url, callback=self.save_file_hwp, meta={'item': item},
                                     dont_filter=True,
                                     headers={
                                         'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'})
            else:
                if file_name.find("pdf") != -1:
                    yield scrapy.Request(file_download_url, callback=self.save_file,
                                         meta={'item': item, 'file_download_url': file_download_url,
                                               'file_name': file_name}, dont_filter=True,
                                         headers={
                                             'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'})
                else:
                    print("###############file does not exist#################")
                    item[config['VARS']['VAR14']] = print_time()
                    yield item
        else:
            print("###############file does not exist#################")
            item[config['VARS']['VAR14']] = print_time()
            yield item

    def save_file(self, response):
        item = response.meta['item']
        print("save_file")

        file_id = self.fs.put(response.body)
        item[config['VARS']['VAR11']] = file_id

        tempfile = NamedTemporaryFile()
        tempfile.write(response.body)
        tempfile.flush()

        extracted_data = parser.from_file(tempfile.name)

        extracted_data = extracted_data["content"]
        if str(type(extracted_data)) == "<class 'str'>":
            extracted_data = CONTROL_CHAR_RE.sub('', extracted_data)
            extracted_data = extracted_data.replace('\n\n', '')
        tempfile.close()
        print(extracted_data)
        item[config['VARS']['VAR12']] = extracted_data
        item[config['VARS']['VAR14']] = print_time()

        yield item

    def save_file_hwp(self, response):
        item = response.meta['item']
        file_id = self.fs.put(response.body)
        item[config['VARS']['VAR11']] = file_id

        tempfile = NamedTemporaryFile()
        tempfile.write(response.body)
        tempfile.flush()

        testPkg = jpype.JPackage('com.argo.hwp')  # get the package
        JavaCls = testPkg.Main  # get the class
        hwp_crawl = JavaCls()  # create an instance of the class
        extracted_data = hwp_crawl.getStringTextFromHWP(tempfile.name)
        if str(type(extracted_data)) == "<class 'str'>":
            extracted_data = CONTROL_CHAR_RE.sub('', extracted_data)
            extracted_data = extracted_data.replace('\n\n', '')
        print(extracted_data)
        print("###############get the hwp content###############")
        tempfile.close()
        item[config['VARS']['VAR12']] = str(extracted_data)
        item[config['VARS']['VAR14']] = print_time()
        yield item
