#import all the necessary libraries
import urllib.request 
from bs4 import BeautifulSoup
import re
import pandas as pd


main_page = 'https://www.worldconferencealerts.com/'
country_page = urllib.request.urlopen(main_page + 'Country.php')
soup = BeautifulSoup(country_page, "lxml")
right_a_tags = soup.find_all('a', class_='btn btn-default state')
all_country_links = [main_page + tag['href'] for tag in right_a_tags]
all_country_links [0:5]

conf1_list = []

for country_link in all_country_links:
    try:
        country_page = urllib.request.urlopen(country_link)
        soup = BeautifulSoup(country_page, "lxml")
        try: total_pages = int(soup.find_all('a', class_='page-link')[-1]['href'].replace('?page=', ''))
        except: total_pages = 0

        for page_number in range(1, total_pages+1):
            page_url = country_link + '?page=' + str(page_number)
            page = urllib.request.urlopen(page_url)
            soup = BeautifulSoup(page, "lxml")

            table = soup.find_all('table', class_='table')

            for entry in table:
                try:
                    date = entry.find('div', class_='date-as-calendar inline-flex size1_5x')['content']
                    reference_link = entry.find('a', class_='conflist')['href']
                    conf_name = entry.find('a', class_='conflist')('span')[0].text
                    location = entry.find('span', class_='div_venue').text.split(',')[0].strip()
                    country = entry.find('span', class_='div_venue').text.split(',')[1].strip()
                    organizer = entry.find('div', class_='organized-by')('a')[0].text
                    category = entry.find('div', class_='organized-by')('a')[1].text.strip()
                    
                    #more information regarding the conference
                    temp_page = urllib.request.urlopen(reference_link)
                    temp_soup = BeautifulSoup(temp_page, "lxml")
                    info = temp_soup.find_all('td', class_ = 'table_content')
                    website = info[2].text.split(' ')[-1].strip()
                    organizer_email = info[3].text.split(' ')[-1].strip()
                    deadline = info[4].text.split(' ')[-1].strip()
                    about_conf =  info[7].text.split('\n\n                                \n')[-1].strip()
                    
                    
                    conf1_list.append([date, reference_link, conf_name, organizer, category, location, country,
                                         website, organizer_email, deadline, about_conf])
                except:
                    continue
    except:
        print("Error in scraping : ", country_link)
        continue


df = pd.DataFrame(conf1_list, columns=['Date', 'Link', 'Name', 'Organizer', 'Category', 'Location', 'Country',
                                        'Website', 'Organizer_Email', 'Deadline', 'About_Conf'])
df.to_csv('conf1.csv', header=True, index=False)
