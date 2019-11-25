import time
import unicodedata

from selenium import webdriver
from bs4 import BeautifulSoup


def parse_article(url, browser):
    browser.get(url)
    page_text = browser.page_source
    page = BeautifulSoup(page_text, 'html.parser')
    title = page.find('title').text.splitlines()[1]
    print(title)
    description = page.find('meta', {'name': 'description'})
    print(description['content'])
    text = ""
    paragraphs = page.find_all('p', {'class': 'hyphenate'})

    for p in paragraphs:
        print(unicodedata.normalize('NFKD', p.get_text()).encode('ascii', 'ignore'))

    print(text)
    print('\n')


def get_articles(browser, limit):
    for i in range(0, limit):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)

    time.sleep(0.5)
    page = BeautifulSoup(browser.page_source, 'html.parser')
    articles_ul = page.find('div', {'class': 'items solrList'})
    articles_links = articles_ul.find_all('a')

    for link in articles_links:
        parse_article(link['href'], browser)


def start():
    browser = webdriver.Chrome("C:/chromedriver.exe")
    browser.get("https://www.onet.pl/")
    categories_ul = browser.find_element_by_class_name('mainMenu').get_attribute('outerHTML')
    categories_ul = BeautifulSoup(categories_ul, 'html.parser')
    links = categories_ul.find_all('a')
    categories_links = []
    for l in links:
        categories_links.append([l.text.strip(), l['href']])
    browser.get(categories_links[0][1])
    get_articles(browser, 5)


start()
