import pandas as pd
import numpy as np
import os
import re
import urllib.request 
from bs4 import BeautifulSoup
import sqlite3

top_university_link = 'https://www.topuniversities.com'

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent':user_agent,} 
request = urllib.request.Request(top_university_link + '/universities/level', None, headers) 
main_page = urllib.request.urlopen(request)
soup = BeautifulSoup(main_page.read(), "lxml")


h2_tags = soup.find_all('h2')
university_names = [h2.text for h2 in h2_tags if not h2.has_attr('class')]
inner_link = soup.find_all('a', class_='profile adv')
print(len(university_names))

uni_courses = {}
for ind, link in enumerate(inner_link):
    request_page = urllib.request.Request("https://www.topuniversities.com" + link['href'], None, headers) 
    coll_page = urllib.request.urlopen(request_page)
    soup2 = BeautifulSoup(coll_page.read(), "lxml")
    
    all_programs = soup2.find_all('a', class_='views-field-title')
    program_names = [pgm.text for pgm in all_programs]
    #country = soup2.find_all('span', class_='country')[0].text
    uni_courses[university_names[ind]] = program_names


uni_courses1 = {college: ';;;'.join(pgms) for college, pgms in uni_courses.items()}
df = pd.DataFrame(uni_courses1.items(), columns=['College', 'Courses'])
df['Courses'].replace('', np.nan, inplace=True)
df.dropna(subset=['Courses'], inplace=True)
df.to_csv('UnivPgms.csv', header=True, index=False)


#Database Update
dataframe = pd.read_csv("UnivPgms.csv")
temp_list = list(map(tuple, dataframe.values))
dataframe.head()


def DB_update(database_path):
    univ_create_table = """ CREATE TABLE IF NOT EXISTS UnivPgms (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                College TEXT NOT NULL,
                Courses TEXT NOT NULL
                ); """
    univ_insert = """INSERT INTO UnivPgms (College, Courses) VALUES(?,?)"""
    
    conn = sqlite3.connect(database_path)
    if conn is not None:
        c = conn.cursor()
        c.execute(univ_create_table)
        for tup in temp_list:
            try: c.execute(univ_insert, tup)
            except: continue
        conn.commit()
        conn.close()
    else:
        print("Error! cannot create the database connection.")
        
if __name__ == '__main__':
    db_path = "KonfHub.db"
    DB_update(db_path)
