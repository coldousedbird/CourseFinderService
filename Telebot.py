# important private data import. All variables are string type
from private_data import Telegram_token, host, user, password, db_name
import telebot      # telebot lib
import pymorphy2    # words normalizing lib
import re           # regular expressions lib
import psycopg2     # PostrgreSQL lib


#Подключаемся к PostgreSQL на сервере
conn = psycopg2.connect(host=host, user=user, password=password, database=db_name)
cursor = conn.cursor()

# Настраиваем язык для библиотеки морфологии
morph = pymorphy2.MorphAnalyzer(lang='ru')

telebot.apihelper.ENABLE_MIDDLEWARE = True

# Укажем token полученный при регистрации бота
bot = telebot.TeleBot(Telegram_token)

# Начнем обработку. Если пользователь запустил бота, ответим
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, "Привет! Напиши, какие курсы тебе интересны?")

# Если пользователь что-то написал, ответим
@bot.message_handler(func=lambda message: True)
def get_text_messages(message):
    msg = message.text

    phrase = re.split ('\W', msg)
    tags = []
    for word in phrase:
        word = morph.parse (word)[0]
        pos = word.tag.POS
        if pos != 'PREP' and pos != 'CONJ' and pos != 'INTJ' and pos != 'PRCL' and pos != 'NPRO' \
                and pos != 'NUMR' and pos != 'INFN' and pos != 'VERB' and pos != 'PRED' \
                and word.normal_form != "" and word.normal_form != "курс":
            tags.append(word.normal_form)
    answers = []
    for tag in tags:
        tag = '%' + tag + '%'
        cursor.execute ("""SELECT answer FROM answers WHERE tags LIKE %s;""", (tag,))
        part_answers = cursor.fetchall ()
        answers = answers + part_answers

    answer = ""
    for part in answers:
        if len (answer) > 3000: break
        answer = answer + part[0] + '\n'
    # выведем в консоль вопрос / ответа
    print ("Запрос:", msg, " \nНормализованный: ", tags, " \nОтвет :", answer)
    if answer != "":
        bot.send_message(message.from_user.id, answer)
    # выведем в консоль вопрос / ответа
    print("Запрос:", msg, " \n\tНормализованный: ", phrase, " \n\t\tОтвет :", answer)

# Запустим обработку событий бота
bot.infinity_polling(none_stop=True, interval=1)

