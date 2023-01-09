import requests
import requests_async
import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
#from price_parser import Price

def find_last_page(soup):
    # Classes are predifined by looking them up on the website
    page_pagination = soup.select('a.Link_link__J4Qd8.Button_base__Pz8U1.Button_inherit___tUxa.Pagination_item__usZku')
    page_numeration = [page_num.find_all('span') for page_num in page_pagination]
    last_page = page_numeration[-1][0].getText()

    return int(last_page)

async def get_item_data(urls):

    async with aiohttp.ClientSession() as session:

        tasks = []
        for url in urls:
            task = asyncio.create_task(requests_async.get(url))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        return responses

link = "https://novi.kupujemprodajem.com/pretraga?keywords=thinkpad&hasPrice=yes&order=price%20desc&page=1"

page = requests.get(link)
soup = BeautifulSoup(page.content, 'html.parser')
last_page = find_last_page(soup)
# Make list of all urls
urls = [link[:-1] + str(i) for i in range(1, last_page + 1)]
all_data = {}

start_time = time.time()
responses = asyncio.run(get_item_data(urls))
print("--- %s seconds ---" % (time.time() - start_time))


# Item counter is neccessary due to same item names occurence
item_counter = 0
for response in responses:
    soup = BeautifulSoup(response.decode('utf-8'), 'html.parser')

    item_names = soup.find_all('div', attrs={'class':'AdItem_name__BppRQ'})
    item_prices = soup.find_all('div', attrs={'class':'AdItem_price__k0rQn'})

    get_item_names = [name.getText() for name in item_names]
    get_item_prices = [price.getText() for price in item_prices]

    for count, name in enumerate(get_item_names):
        all_data[str(item_counter + count) + name] = get_item_prices[count]

    item_counter += len(get_item_names)

print(len(all_data))
