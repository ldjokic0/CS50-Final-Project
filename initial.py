from bs4 import BeautifulSoup
import requests

# Search items and prices based on the class

# TODO
# Search all pages based on keywords - category - price with descanding order of prices
page = requests.get("https://novi.kupujemprodajem.com/kompjuteri-laptop-i-tablet/pretraga?keywords=thinkpad&categoryId=1221&hasPrice=yes&order=price%20desc&page=1")
soup = BeautifulSoup(page.content, 'html.parser')

items_name = soup.find_all('div', attrs={'class':'AdItem_name__BppRQ'})
item_prices = soup.find_all('div', attrs={'class':'AdItem_price__k0rQn'})

print(type(items_name), type(item_prices))