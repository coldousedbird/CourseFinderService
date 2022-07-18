import pymorphy2    # words normalizing lib
import re           # regular expressions lib

import psycopg2     # PostrgreSQL lib
import requests     # site reading lib
from bs4 import BeautifulSoup
from private_data import Telegram_token, host, user, password, db_name


def parser(url, description, tags):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    bunch_of_text = soup.find_all('div', class_='listcot col-md-9 col-sm-9 col-xs-9')
    bunch_of_a = [c.a for c in bunch_of_text]
    # full description
    for c in bunch_of_a:
        description.append(c.text + "\n" + c['href'])
    # description = [c.text + " " + c['href'] for c in bunch_of_a] # - earlier version

    # turn description text into tags
    text = [c.text for c in bunch_of_a]
    morph = pymorphy2.MorphAnalyzer(lang='ru')
    #if morph.parse("1000")[0].tag.string.consist('NUMB'): print("ye")
    for i in range(len(text)):
        phrase = re.split('\W', text[i])
        tags.append("")
        for word in phrase:
            word = morph.parse(word)[0]
            pos = word.tag.POS
            if pos != 'PREP' and pos != 'CONJ' and pos != 'INTJ' and pos != 'PRCL' \
                    and pos != 'NUMR' and pos != 'INFN' and pos != 'VERB':
                tags[i] = tags[i] + word.normal_form + " "


def db_input(description, tags):
    # Подключаемся к PostgreSQL на сервере
    connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    for i in range(len(description)):
        with connection.cursor() as cursor:
            connection.autocommit = True
            cursor.execute("""INSERT INTO answers (answer, tags) VALUES (%s, %s);""", (description[i], tags[i],))


# Parsing site
url = 'https://vse-kursy.com/onlain/free/?ysclid=l55k1ui5n9366579259'
desc = []
tags = []
parser(url, desc, tags)
db_input(desc, tags)

url = 'https://vse-kursy.com/onlain/free/page/'
for i in range(2, 54):
    url_cycle = url + str(i) + "/"
    desc = []
    tags = []
    parser (url_cycle, desc, tags)
    db_input (desc, tags)
    print (url_cycle, " is done")