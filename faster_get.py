import requests
import time
from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup

def find_last_page(soup):
    # Classes are predifined by looking them up on the website
    page_pagination = soup.select('a.Link_link__J4Qd8.Button_base__Pz8U1.Button_inherit___tUxa.Pagination_item__usZku')
    page_numeration = [page_num.find_all('span') for page_num in page_pagination]
    last_page = page_numeration[-1][0].getText()

    return int(last_page)

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
    

if __name__=='__main__':

    link = "https://novi.kupujemprodajem.com/pretraga?keywords=thinkpad&hasPrice=yes&order=price%20desc&page=1"

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    last_page = find_last_page(soup)
    # Make list of all urls
    urls = [link[:-1] + str(i) for i in range(1, last_page + 1)]
    all_data = {}

    start_time = time.time()
    responses = get_all_url_data(urls)
    print(f'Fetch total {last_page} urls and process takes {time.time() - start_time} seconds')

    item_counter = 0
    for response in responses:

        soup = BeautifulSoup(response, 'html.parser')

        item_names = soup.find_all('div', attrs={'class':'AdItem_name__BppRQ'})
        item_prices = soup.find_all('div', attrs={'class':'AdItem_price__k0rQn'})

        get_item_names = [name.getText() for name in item_names]
        get_item_prices = [price.getText() for price in item_prices]

        for count, name in enumerate(get_item_names):
            all_data[str(item_counter + count) + name] = get_item_prices[count]

        item_counter += len(get_item_names)

    print(len(all_data))