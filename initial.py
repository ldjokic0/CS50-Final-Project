from bs4 import BeautifulSoup
import requests
import time
#from price_parser import Price

def find_last_page(soup):
    # Classes are predifined by looking them up on the website
    page_pagination = soup.select('a.Link_link__J4Qd8.Button_base__Pz8U1.Button_inherit___tUxa.Pagination_item__usZku')
    page_numeration = [page_num.find_all('span') for page_num in page_pagination]
    last_page = page_numeration[-1][0].getText()

    return int(last_page)

# TODO
# Search all pages based on keywords - category - price with descanding order of prices
### First iteration of the program will just search all pages and add items and their prics to dict

link = "https://novi.kupujemprodajem.com/pretraga?keywords=thinkpad&hasPrice=yes&order=price%20desc&page=1"

page = requests.get(link)
soup = BeautifulSoup(page.content, 'html.parser')

all_data = {}

# Item counter is neccessary due to same item names occurence
item_counter = 0
last_page = find_last_page(soup)

start_time = time.time()

for i in range(1, 100):
    
    start_time = time.time()
    link = "https://novi.kupujemprodajem.com/pretraga?keywords=thinkpad&hasPrice=yes&order=price%20desc&page=" + str(i)
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    print("--- %s seconds ---" % (time.time() - start_time))

    item_names = soup.find_all('div', attrs={'class':'AdItem_name__BppRQ'})
    item_prices = soup.find_all('div', attrs={'class':'AdItem_price__k0rQn'})

    get_item_names = [name.getText() for name in item_names]
    get_item_prices = [price.getText() for price in item_prices]

    for count, name in enumerate(get_item_names):
        all_data[str(item_counter + count) + name] = get_item_prices[count]

    item_counter += len(get_item_names)

print("--- %s seconds ---" % (time.time() - start_time))
#print(len(all_data.values()))
#print(all_data)

### Utilize later to distinguish prices from eur and rsd
#price = Price.fromstring(get_item_prices[count])