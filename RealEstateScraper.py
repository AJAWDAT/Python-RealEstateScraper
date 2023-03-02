"""Exports the information for a location from Foxtons website to a csv file."""

import os
import csv
import threading
from bs4 import BeautifulSoup
import requests

# User must enter their desired paths.
os.makedirs("C:\\Users\\Ahmed\\Desktop\\RealEstate", exist_ok=True)
os.chdir("C:\\Users\\Ahmed\\Desktop\\RealEstate")

property_info_csv_file = open('property_info.csv', 'w', newline='')
property_dictionary_writer = csv.DictWriter(property_info_csv_file, ['Address',
                                                                     'Property Type',
                                                                     'Per Week',
                                                                     'Bedrooms',
                                                                     'Bathrooms',
                                                                     'Property Link'])
property_dictionary_writer.writeheader()
search_location = input('Please enter an area to scrape house price data for.')
estate_agent_url = 'https://www.foxtons.co.uk/properties-to-rent/' + search_location

res = requests.get(estate_agent_url, timeout=5)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

list_of_property_links = []
for i in soup.find_all('a', href=True):
    if i['href'].startswith('/properties-to-rent/'):
        if i['href'][-4:].isnumeric():
            if i['href'] not in list_of_property_links:
                list_of_property_links.append(i['href'])

print(len(list_of_property_links))
print(list_of_property_links)


def property_link_info_extractor(property_link):
    """Extracts the information from each property link supplied to the argument"""
    property_info = {'address': None,
                     'property_type': None,
                     'per week': None,
                     'bedrooms': None,
                     'bathrooms': None,
                     'property_link': property_link}

    # Creat soup
    res_property = requests.get(property_link, timeout=5)
    res_property.raise_for_status()
    soup_property = BeautifulSoup(res_property.text, "html.parser")

    # Find the address
    property_address_element = soup_property.find('h1')
    if str(property_address_element) == '<h1>Sneak Peek</h1>':
        res_property.close()
        return

    property_info['address'] = str(property_address_element)[4:-5]

    # Find the property type
    property_type_element = soup_property.find('div', {'class': 'property-info'})
    property_type = property_type_element.findAll('span')
    property_info['property_type'] = str(property_type[0])[20:-7]
    if property_info['property_type'] == ('Parking space' or 'Garage'):
        return

    # Find the price per week
    price_per_week_element = soup_property.find('h2', {'class': 'price price-mobile'})
    price_per_week = price_per_week_element.findAll('data')
    property_info['per week'] = str(price_per_week[0])[6:-8]

    # Find the number of bedrooms and bathrooms
    bedroom_bathroom_element = soup_property.findAll('div', {'class': 'property-stats'})
    if property_info['property_type'] == 'Studio':
        property_info['bedrooms'] = 1
    else:
        bedroom_number = bedroom_bathroom_element[0].findAll('span')
        property_info['bedrooms'] = str(bedroom_number[0])[6:-7]
    bathroom_number = bedroom_bathroom_element[1].findAll('span')
    property_info['bathrooms'] = str(bathroom_number[0])[6:-7]
    print(property_info)
    # Close request
    res_property.close()
    property_dictionary_writer.writerow({'Address': property_info['address'],
                                         'Property Type': property_info['property_type'],
                                         'Per Week': property_info['per week'],
                                         'Bedrooms': property_info['bedrooms'],
                                         'Bathrooms': property_info['bathrooms'],
                                         'Property Link': property_info['property_link']
                                         })

# Using threads to make the process faster.
threads_extract_property_info = []
for k, link in enumerate(list_of_property_links):
    property_k_url = 'https://www.foxtons.co.uk' + link
    extract_property_info_thread = threading.Thread(target=property_link_info_extractor,
                                                    args=(property_k_url,))
    threads_extract_property_info.append(extract_property_info_thread)
    extract_property_info_thread.start()

for extract_property_info_thread in threads_extract_property_info:
    extract_property_info_thread.join()

res.close()
property_info_csv_file.close()
