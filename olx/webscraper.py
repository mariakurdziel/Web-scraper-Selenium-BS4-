# -*- coding: utf-8 -*-
import csv
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver

from olx.offer import Offer

def write_to_csv(list_of_offers):
    with open('offers.csv', 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['title', 'location', 'time_of_work', 'type_of_agreement', 'salary', 'article_url']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for o in list_of_offers:
            writer.writerow(
                {'title': o.title, 'location': o.location, 'time_of_work': o.time_of_work, 'type_of_agreement': o.type_of_agreement, 'salary': o.salary, 'article_url': o.article_url })

def parse_articles(browser, url):
    list_of_offers = []
    browser.get(url)
    page = BeautifulSoup(browser.page_source, 'html.parser')
    link_element = page.find_all('a',  {'class': 'marginright5 link linkWithHash detailsLink'})
    salaries = page.find_all('div', {'class': 'list-item__price'})
    locations = page.find_all('small', {'class': 'breadcrumb x-normal'})
    times_of_work = page.find_all('small',  {'class': 'breadcrumb breadcrumb--job-type x-normal'})
    types_of_agreements = page.find_all('small', {'class': 'breadcrumb breadcrumb--with-divider x-normal'})
    for i in range(0, len(link_element)):
        offer_url = link_element[i]['href']
        title = link_element[i].text.strip()
        salary = salaries[i].text.strip()
        location = locations[i].text.strip()
        time_of_work = times_of_work[i].text.strip()
        type_of_agreement = types_of_agreements[i].text.strip()
        offer = Offer(title, location, time_of_work,type_of_agreement, salary,offer_url)
        list_of_offers.append(offer)

    return list_of_offers




def get_offers(browser, page_links):
    list_of_offers = []
    for p in page_links:
        list_of_offers += parse_articles(browser,p)

    write_to_csv(list_of_offers)


def get_links(browser, search_url):
    list_of_links = [search_url]
    browser.get(search_url)
    link_elements = browser.find_elements_by_xpath('//*[@id="body-container"]/div[3]/div/div[8]/span/a')
    link_elements.pop()
    for l in link_elements:
        list_of_links.append(l.get_attribute('href'))
    return list_of_links


def fill_form(browser, city, category, type_of_agreement):
    if category == 'i':
        category = 'IT / telekomunikacja'
    elif category == 'b':
        category = 'Budowa / remonty'
    elif category == 'g':
        category = 'Gastronomia'
    elif category == 'a':
        category = 'Administracja biurowa'

    if type_of_agreement == 'a':
        xpath = '//*[@id="f-part_contract"]'
    elif type_of_agreement == 'b':
        xpath = '//*[@ id = "param_contract"]/div/ul/li[3]/label[2]'
    elif type_of_agreement == 'c':
        xpath = '//*[@id="param_contract"]/div/a/span[1]'

    show_all = browser.find_element_by_xpath('//*[@id="topLinkShowAll"]/span/span')
    browser.execute_script("arguments[0].click()", show_all)
    category = browser.find_element_by_link_text(category)
    browser.get(category.get_attribute('href'))
    browser.find_element_by_id('cityField').send_keys(city)
    browser.find_element_by_xpath('//*[@id="param_contract"]/div/a/span[1]').click()
    sleep(0.5)
    browser.find_element_by_xpath(xpath).click()
    browser.find_element_by_id('search-submit').click()
    sleep(1)
    print(browser.current_url)
    return browser.current_url


def start():
    browser = webdriver.Chrome("C:/chromedriver.exe")
    browser.get("https://www.olx.pl/praca/")

    print('Wpisz miasto')
    city = input()
    print('Wybierz specjalność: i - IT, g - Gastronomia, b - Budownictwo, a - Administracja')
    category = input()
    print('Wybierz czas pracy: a - umowa o pracę, b - umowa o dzieło, c - umowa zlecenie')
    type_of_agreement = input()
    search_url = fill_form(browser, city, category, type_of_agreement)
    page_links = get_links(browser, search_url)
    get_offers(browser, page_links)


start()
