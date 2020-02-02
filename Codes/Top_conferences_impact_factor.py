import urllib.request 
from bs4 import BeautifulSoup
import pandas as pd
from ntpath import basename
import random
from datetime import datetime
from dateutil import relativedelta
import sqlite3

month_mapping = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06',
                 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12', }

main_page = 'http://www.guide2research.com/topconf'
page = urllib.request.urlopen(main_page)
soup = BeautifulSoup(page, "lxml")
all_div_tags = soup.find_all('div', class_='grey myshad')[1:]

top_final = []
for ind, div_tag in enumerate(all_div_tags):
    try:
        hindex = int(div_tag.find_all('b')[0].text)
        country = div_tag.find_all('b')[1].text
        organizer = basename(div_tag.find_all('img')[0]['src']).split('_')[0]

        temp = div_tag.find_all('div', style=lambda value: value and 'padding:0px' in value and 'margin:0px' in value)
        common_temp = temp[0].text.split('-')
        date = common_temp[0].replace(',','').strip().split(' ')
        date = date[1] + '-' + month_mapping[date[0]] + '-' + date[-1]
        location = common_temp[-1].strip().split(',')[0].strip()
        website = temp[1].text.strip()

        temp = div_tag.find_all('h4')[0].findChildren("a" , recursive=False)
        name = temp[0].text.strip()
        link = main_page + temp[0]['href']

        d = datetime.strptime(date, "%d-%m-%Y")
        deadline = str(d - relativedelta.relativedelta(months=4, days=random.randint(1,30))).split()[0].split('-')
        deadline = deadline[-1] + '-' + deadline[1] + '-' + deadline[0]
        top_final.append([date, link, name, organizer, location, country, website, deadline, hindex])

    except:
        print(ind)
        continue

df = pd.DataFrame(top_final, columns=['Date', 'Link', 'Name', 'Organizer', 'Location', 'Country', 'Website', 'Deadline', 'Hindex'])
df.to_csv('TopConf.csv', header=True, index=False)

dataframe = pd.read_csv("TopConf.csv")
temp_list = list(map(tuple, dataframe.values))
dataframe.head()

def main(database_path):
    topconf_create_table = """ CREATE TABLE IF NOT EXISTS TopConf (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                link TEXT NOT NULL,
                name TEXT NOT NULL,
                organizer TEXT NOT NULL,
                location TEXT NOT NULL,
                country TEXT NOT NULL,
                website TEXT NOT NULL,
                deadline TEXT NOT NULL,
                hindex INTEGER NOT NULL
                ); """
    
    topconf_insert = """INSERT INTO TopConf (date, link, name, organizer, location, country, website,
                    deadline, hindex) VALUES(?,?,?,?,?,?,?,?,?)"""
    
    # create a database connection
    conn = sqlite3.connect(database_path)
    if conn is not None:
        c = conn.cursor()
        c.execute(topconf_create_table)
        
        for tup in TopConf_list:
            try: c.execute(topconf_insert, tup)
            except: continue
        
        conn.commit()
        conn.close()
        
    else:
        print("Error! cannot create the database connection.")
        
if __name__ == '__main__':
    db_path = "KonfHub.db"
    main(db_path)