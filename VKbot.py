# important private data import. All variables are string type
from private_data import VK_token, host, user, password, db_name

# vk_api libs
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import pymorphy2    # words normalizing lib         # pip install pymorphy2
import re           # regular expressions lib       #
import psycopg2     # PostrgreSQL lib               #  pip install psycopg2


def sender(id, text):
    try:
        vk.messages.send(user_id = id, message = text, random_id = 0)
    except: print('we fucked up')

def err_send(id):
    sender(id, "Простите, я вас не понял")

#def send_stick (id, number):
#    vk.messages.send(user_id = id, sticker_id = number, random_id = 0)
#def send_photo (id, url):
#    vk.messages.send(user_id = id, attachment = url, random_id = 0)

# Настраиваем язык для библиотеки морфологии
morph = pymorphy2.MorphAnalyzer(lang='ru')


# Подключаемся к PostgreSQL на сервере
conn = psycopg2.connect(host=host, user=user, password=password, database=db_name)
cursor = conn.cursor()


vk_session = vk_api.VkApi(token = VK_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        msg = event.text.lower()
        id = event.user_id

        phrase = re.split('\W', msg)
        tags = []
        for word in phrase:
            word = morph.parse(word)[0]
            pos = word.tag.POS
            if pos != 'PREP' and pos != 'CONJ' and pos != 'INTJ' and pos != 'PRCL' and pos != 'NPRO'\
                    and pos != 'NUMR' and pos != 'INFN' and pos != 'VERB' and pos != 'PRED'\
                    and word.normal_form != "" and word.normal_form != "курс":
                tags.append(word.normal_form)
        answers = []
        for tag in tags:
            tag = '%' + tag + '%'
            cursor.execute("""SELECT answer FROM answers WHERE tags LIKE %s;""", (tag,))
            part_answers = cursor.fetchall()
            answers = answers + part_answers


        answer = ""
        for part in answers:
            if len(answer) > 3000: break
            answer = answer + part[0] + '\n'
        # выведем в консоль вопрос / ответа
        print("Запрос:", msg, " \nНормализованный: ", tags, " \nОтвет :", answer)
        if answer != "":
            sender(id, answer)

        # just an example
        # if msg == "привет":
        #     sender(id,"ohayo")
        #     #send_stick(id, 11238)
        # else: err_send(id)


