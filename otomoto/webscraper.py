import time
import csv
from selenium import webdriver
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

from otomoto.article import Article


def write_to_csv(list_of_articles):
    with open('cars.csv', 'w', newline='') as csv_file:
        fieldnames = ['model', 'production year', 'mileage', 'engine capacity', 'price', 'currency', 'city', 'region']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for a in list_of_articles:
            writer.writerow({'model': a.model_name, 'production year': a.production_year, 'mileage': a.mileage,
                             'engine capacity': a.engine_capacity, 'price': a.price, 'currency': a.currency,
                             'city': a.city, 'region': a.region})


def parse_page_source(body):
    list_of_articles = []
    body = BeautifulSoup(body, 'html.parser')
    articles = body.find_all('article')
    for article in articles:
        name = article.find('a', {'class': 'offer-title__link'}).text.strip()
        ul_element = article.find('ul')
        general_infos = ul_element.find_all('li')
        production_year = general_infos[0].text.strip()
        mileage = general_infos[1].text.strip()
        engine_capacity = general_infos[2].text.strip()
        price_infos = article.find('div', {'class': 'offer-price ds-price-block'})
        price = price_infos.find('span', {'class': 'offer-price__number ds-price-number'}).find('span').text.strip()
        currency = price_infos.find('span', {'class': 'offer-price__currency ds-price-currency'}).text.strip()
        city = article.find('span', {'class': 'ds-location-city'}).text.strip()
        region = article.find('span', {'class': 'ds-location-region'}).text.strip()
        region = region[1:len(region) - 1]
        list_of_articles.append(Article(name, production_year, mileage, engine_capacity, price, currency, city, region))

    return list_of_articles


def parse_data(number_of_pages, base_url, browser):
    list_of_articles = []
    list_of_articles += (parse_page_source(browser.page_source))

    for page in range(2, number_of_pages+1):
        url = base_url + str(page)
        browser.get(url)
        list_of_articles += (parse_page_source(browser.page_source))

    write_to_csv(list_of_articles)

def fill_form():
    options = Options()
    options.headless = True
    browser = webdriver.Chrome("C:/chromedriver.exe", options=options)
    browser.get("https://www.otomoto.pl/")
    browser.find_element_by_link_text('Osobowe').click()
    time.sleep(0.4)
    select_brand = Select(browser.find_element_by_id('param571'))
    select_brand.select_by_value('opel')
    select_model = Select(browser.find_element_by_id('param573'))
    select_model.select_by_visible_text('Corsa')
    select_min_price = Select(browser.find_element_by_xpath("//*[@id='searchmain_29']/div[4]/span[1]/select"))
    select_min_price.select_by_value('2000')
    select_max_price = Select(browser.find_element_by_xpath("//*[@id='searchmain_29']/div[4]/span[2]/select"))
    select_max_price.select_by_value('20000')
    select_min_production_year = Select(browser.find_element_by_xpath("//*[@id='searchmain_29']/div[5]/span[1]/select"))
    select_min_production_year.select_by_value('2009')
    select_max_production_year = Select(browser.find_element_by_xpath("//*[@id='searchmain_29']/div[5]/span[2]/select"))
    select_max_production_year.select_by_value('2019')
    select_min_mileage = Select(browser.find_element_by_xpath("//*[@id='searchmain_29']/div[6]/span[1]/select"))
    select_min_mileage.select_by_value('75000')
    select_max_mileage = Select(browser.find_element_by_xpath("//*[@id='searchmain_29']/div[6]/span[2]/select"))
    select_max_mileage.select_by_value('150000')
    fuel_type = browser.find_element_by_xpath("//*[@id='searchmain_29']/div[7]/span[2]")
    fuel_type.click()
    search_button = browser.find_element_by_xpath("//*[@id='searchmain_29']/button[1]/span[1]")
    browser.execute_script("arguments[0].click();", search_button)
    time.sleep(0.5)
    site_pages = browser.find_element_by_xpath("//*[@id='body-container']/div[2]/div[2]/ul").get_attribute('outerHTML')
    site_pages = BeautifulSoup(site_pages, 'html.parser')
    pages = site_pages.find_all('span', {'class': 'page'})
    number_of_pages = int(pages[len(pages) - 1].text.strip())
    page_link = site_pages.find('a', href=True)['href']
    base_url = page_link[0:len(page_link)-1]
    parse_data(number_of_pages, base_url, browser)


fill_form()
