# -*- coding: utf-8 -*-
import csv
import random
import string
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import requests

from onet.article import Article


def write_to_csv(list_of_articles):
    with open('articles.csv', 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['title', 'description', 'text', 'image name']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for a in list_of_articles:
            writer.writerow(
                {'title': a.title, 'description': a.description, 'text': a.text, 'image name': a.image_name})


def scrape_image(url, image_name):
    response = requests.get('http:' + url)
    if response.status_code == 200:
        with open('./images/' + image_name, 'wb') as f:
            f.write(response.content)


def set_image_name():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + '.jpg'


def parse_article(url, browser):
    browser.get(url)
    page = BeautifulSoup(browser.page_source, 'html.parser')
    title = page.find('title').text.splitlines()[1]
    description = page.find('meta', {'name': 'description'})
    text = ""
    paragraphs = page.find_all('p', {'class': 'hyphenate'})

    for p in paragraphs:
        text += p.text + '\n'

    image_url = page.find('picture')

    if image_url is not None:
        image_url = BeautifulSoup(str(image_url), 'html.parser')
        img = image_url.find('img')
        image_name = img['src'].rsplit('/', 1)[1]
        if image_name == '.jpg':
            image_name = set_image_name()

        scrape_image(img['src'], image_name)
    else:
        image_name = "No image found"

    return Article(title, description['content'], text, image_name)


def get_articles(browser, limit):
    list_of_articles = []
    articles_links = []

    while len(articles_links) < limit:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)
        page = BeautifulSoup(browser.page_source, 'html.parser')
        articles_ul = page.find('div', {'class': 'items solrList'})
        articles_links = articles_ul.find_all('a')

    articles_links = articles_links[0: limit]

    for link in articles_links:
        list_of_articles.append(parse_article(link['href'], browser))

    return list_of_articles


def get_category_url(category, browser):
    if category == 'k':
        category_name = 'Kultura'
    elif category == 'w':
        category_name = 'Wiadomości'
    elif category == 's':
        category_name = 'Sport'

    categories_ul = browser.find_element_by_class_name('mainMenu').get_attribute('outerHTML')
    categories_ul = BeautifulSoup(categories_ul, 'html.parser')
    links = categories_ul.find_all('a')

    for l in links:
        if l.text.strip() == category_name:
            print(l['href'])
            return l['href']

    return "Not found"


def start():
    browser = webdriver.Chrome("C:/chromedriver.exe")
    browser.get("https://www.onet.pl/")

    print('Wybierz kategorię newsów: w - Wiadomości, k - Kultura, s - Sport')
    category = input()
    print('Wpisz ilość newsów:')
    number = input()
    url = get_category_url(category, browser)
    browser.get(url)
    list_of_articles = get_articles(browser, int(number))
    write_to_csv(list_of_articles)


start()
