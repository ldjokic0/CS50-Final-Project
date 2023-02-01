import requests
import time
from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup
from price_parser import Price


class Item:
    def __init__(self, name, price, page):
        self.name = name
        self.price = price
        self.page = page


# Get current exchange rate for RSD to EUR
def current_exchange_rate():

    # If there is problem with loading page, aproximate exchange rate will be used
    try:
        page = requests.get("https://www.kursna-lista.info/valuta/eur-evro")
    except requests.exceptions.RequestException as e:
        return 117.5

    soup = BeautifulSoup(page.content, 'lxml')
    element_by_id = soup.find('div', {'id': 'largeDisplay'})
    find_p = element_by_id.find_all('p')

    current_exchange_rate_string = find_p[0].getText()
    strings = current_exchange_rate_string.split()
    # Third string in list 'strings' is the middle exchage rate
    rate = float(strings[3].replace(',', '.'))

    return rate


# Convert strings to prices
def adjust_price(price_string):
    price_and_currency = Price.fromstring(price_string)
    if price_and_currency.currency == '€':
        return float(price_and_currency.amount)
    else:
        # Slows down search due to conversion, alternative is to define constant value for exchange rate
        return round(float(price_and_currency.amount) / 117.5, 2)
        #return round(float(price_and_currency.amount) / current_exchange_rate(), 2)


def kp_find_last_page(soup):
    # Classes are predifined by looking them up on the kupujemprodajem website
    page_pagination = soup.select('a.Link_link__J4Qd8.Button_base__Pz8U1.Button_inherit___tUxa.Pagination_item__usZku')
    page_numeration = [page_num.find_all('span') for page_num in page_pagination]

    # Check if there is just one page
    if page_numeration:
        last_page = page_numeration[-1][0].getText()
        return int(last_page)
    else:
        last_page = 1

    return last_page


def fetch_url_data(pg_url):
    try:
        resp = requests.get(pg_url)
    except Exception as e:
        print(f"Error occured during fetch data from url{pg_url}")
    else:
        return resp.content


def get_all_url_data(url_list):
    with ProcessPoolExecutor() as executor:
        resp = executor.map(fetch_url_data, url_list)
    return resp


def get_items(responses):
    # Empty dictionary that will contain name and price of the items
    item_list = []
    item_counter, page_num = 0, 1

    start_time = time.time()
    for response in responses:

        soup = BeautifulSoup(response, 'html.parser')

        item_names = soup.find_all('div', attrs={'class': 'AdItem_name__80tI5'})
        item_prices = soup.find_all('div', attrs={'class': 'AdItem_price__jUgxi'})

        get_item_names = [name.getText() for name in item_names]
        get_item_prices = [price.getText() for price in item_prices]

        for count, name in enumerate(get_item_names):
            price = adjust_price(get_item_prices[count])
            item_list.append(Item(name, price, page_num))

        item_counter += len(get_item_names)
        page_num += 1

    total_time = "%s seconds" % (time.time() - start_time)

    return item_list, item_counter, total_time


def kp_search(keyword):
    # Check and replace spaces in keyword
    keyword = keyword.replace(' ', '%20')
    # Predefined link for kupujemprodajem website
    link = f"https://novi.kupujemprodajem.com/pretraga?keywords={keyword}&hasPrice=yes&order=price%20desc&page=1"

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    last_page = kp_find_last_page(soup)
    # Make list of all urls that will be searched
    urls = [link[:-1] + str(i) for i in range(1, last_page + 1)]

    responses = get_all_url_data(urls)
    items, item_count, _ = get_items(responses)

    return items, item_count


""" if __name__ == '__main__':
    items, item_count = kp_search("Dell Latitude E6540")
    print(item_count)
    for item in items:
        print(item.name, item.price) """
