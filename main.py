import telebot
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
from telebot import types
import threading

telebot.apihelper.ENABLE_MIDDLEWARE = True

bot = telebot.TeleBot("5840219241:AAEBfeIlrwCH6g9ZElRe4PnJogqkV7EpHfo")

user_data = {}

visit = None
number = None
mail = None
user_name = None
language = None

SAMPLE_RANGE_NAME = 'list1!A1:B3'


class GoogleSheet:
    SPREADSHEET_ID = '1O4qRSIi3wXqC87j49lIGt_U0if7oxR2rZqFuloVJXDY'

    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
        self.lock = threading.Lock()
        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e1:
                    print(e1)
                    creds = None

            if not creds:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
        self.service = build('sheets', 'v4', credentials=creds)

    def updaterangevalues(self, range_name, test_values):
        data = [{
            'range': range_name,
            'values': test_values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        try:
            with self.lock:
                result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                          body=body).execute()
                print('{0} cells updated.'.format(result.get('totalUpdatedCells')))
        except Exception as e1:
            print(e1)


def main():
    if user_name is not None and number is not None and  and visit is not None:
        gs = GoogleSheet()

        test_values = [
            [user_name,
             number,

             visit]
        ]
        values = gs.service.spreadsheets().values().get(spreadsheetId=gs.SPREADSHEET_ID,
                                                        range=SAMPLE_RANGE_NAME).execute().get('values', [])
        if not values:
            start_row = 1

        else:
            start_row = len(values) + 1
        end_row = start_row + len(test_values) - 1
        range_name = f"list1!A{start_row}:D{end_row}"
        gs.updaterangevalues(range_name, test_values)


if __name__ == '__main__':
    main()


@bot.message_handler(commands=["start"])
def start(message):
    try:

        global language

        language = message.text.strip()
        markup = types.InlineKeyboardMarkup()
        ru_button = types.InlineKeyboardButton("Русский", callback_data="ru")
        ro_button = types.InlineKeyboardButton("Română", callback_data="ro")
        en_button = types.InlineKeyboardButton("english", callback_data="en")
        markup.add(ru_button, ro_button, en_button)
        bot.send_message(message.chat.id, "Выберите язык / Alegeți limba de comunicare/"
                                          "choose communication language :", reply_markup=markup)
        bot.register_next_step_handler(message, callback_query)

    except Exception as err:
        print(err)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(callback_queryq):
    global language

    chat_id = callback_queryq.message.chat.id

    if callback_queryq.data == "ru":
        language = "ru"
        bot.send_message(chat_id, "Язык изменён на русский")
        bot.register_next_step_handler(callback_queryq.message, get_name_ru)
        bot.send_message(chat_id, "Привет! Как вас зовут?")

    elif callback_queryq.data == "ro":
        language = "ro"
        bot.send_message(chat_id, "Limba schimbata la romana")
        bot.send_message(chat_id, "Bună ziua! Introduceti numele dvs.?")
        bot.register_next_step_handler(callback_queryq.message, get_name_ro)

    elif callback_queryq.data == "en":
        language = "en"
        bot.send_message(chat_id, "Language changed to english")
        bot.send_message(chat_id, "enter your name")
        bot.register_next_step_handler(callback_queryq.message, get_name_en)


def get_name_ru(message):
    try:

        global user_name

        name_u = message.text.strip()
        user_name = name_u
        chat_id = message.chat.id
        user_data[chat_id] = {'name_U': name_u,
                              'phone_number': None,
                              'email': None,
                              'visit_reason': None
                              }

        bot.reply_to(message, f"Приятно познакомиться, {name_u}! Какова цель вашего визита?")

        markup = get_visit_reason_markup_ru()
        bot.send_message(chat_id, "Выберите причину визита:", reply_markup=markup)

        bot.register_next_step_handler(message, get_visit_reason_ru)

    except Exception as err:
        print(err)


def get_name_ro(message):
    try:

        global user_name

        name_u = message.text.strip()
        user_name = name_u
        chat_id = message.chat.id

        user_data[chat_id] = {'name_U': name_u,
                              'phone_number': None,
                              'email': None,
                              'visit_reason': None
                              }

        bot.reply_to(message, f"încântat de cunoştinţă, {name_u}! care este scopul vizitei dvs?",
                     reply_markup=get_visit_reason_markup_ro())
        bot.register_next_step_handler(message, get_visit_reason_ro)

    except Exception as err:
        print(err)


def get_name_en(message):
    try:

        global user_name

        name_u = message.text.strip()
        user_name = name_u
        chat_id = message.chat.id
        user_data[chat_id] = {'name_U': name_u,
                              'phone_number': None,
                              'email': None,
                              'visit_reason': None
                              }

        bot.reply_to(message, f"Nice to meet you, {name_u}! Whats your visit reason?")

        markup = get_visit_reason_markup_en()
        bot.send_message(chat_id, "Choose visit reason:", reply_markup=markup)

        bot.register_next_step_handler(message, get_visit_reason_en)

    except Exception as err:
        print(err)


def get_visit_reason_ru(message):
    try:

        global visit

        visit_reason = message.text.strip()
        visit = visit_reason
        chat_id = message.chat.id
        user_data[chat_id]['visit_reason'] = visit_reason

        if visit_reason == "Ознакомление":
            msg = bot.send_message(chat_id, "Вы выбрали ознакомление. Напишите ваш номер телефона.",
                                   reply_markup=get_remove_keyboard_markup())
            bot.register_next_step_handler(msg, get_phone_number_ru)

        elif visit_reason == "Сотрудничество":
            msg = bot.send_message(chat_id, "Вы выбрали сотрудничество. Напишите ваш номер телефона.",
                                   reply_markup=get_remove_keyboard_markup())
            bot.register_next_step_handler(msg, get_phone_number_ru)

        else:
            msg = bot.send_message(chat_id, "Пожалуйста, выберите один из вариантов ниже.",
                                   reply_markup=get_visit_reason_markup_ru())
            bot.register_next_step_handler(msg, get_visit_reason_ru)

    except Exception as err:
        print(err)


def get_visit_reason_markup_ru():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Ознакомление')
    itembtn2 = types.KeyboardButton('Сотрудничество')
    markup.add(itembtn1, itembtn2)
    return markup


def get_visit_reason_ro(message):
    try:

        global visit

        visit_reason = message.text.strip()
        visit = visit_reason
        chat_id = message.chat.id
        user_data[chat_id]['visit_reason'] = visit_reason

        if visit_reason == "familiarizarea":
            bot.send_message(chat_id, "ati ales o familiarizarea, introduceti numarul de telefon.",
                             reply_markup=get_remove_keyboard_markup())
            bot.register_next_step_handler(message, get_phone_number_ro)

        elif visit_reason == "cooperare":
            bot.send_message(chat_id, "ati ales cooperarea, introduceti numarul de telefon.",
                             reply_markup=get_remove_keyboard_markup())

            bot.register_next_step_handler(message, get_phone_number_ro)

        else:
            bot.send_message(chat_id, "vă rugăm să selectați una dintre opțiunile de mai jos.",
                             reply_markup=get_visit_reason_markup_ro())
            bot.register_next_step_handler(message, get_visit_reason_ro)

    except Exception as err:
        print(err)


def get_visit_reason_markup_ro():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('familiarizarea')
    itembtn2 = types.KeyboardButton('cooperarea')
    markup.add(itembtn1, itembtn2)
    return markup


def get_visit_reason_en(message):
    try:

        global visit

        visit_reason = message.text.strip()
        visit = visit_reason
        chat_id = message.chat.id
        user_data[chat_id]['visit_reason'] = visit_reason

        if visit_reason == "familiarization":
            msg = bot.send_message(chat_id, "You choose familiarization. Enter your phone number.",
                                   reply_markup=get_remove_keyboard_markup())
            bot.register_next_step_handler(msg, get_phone_number_en)

        elif visit_reason == "cooperation":
            msg = bot.send_message(chat_id, "You choose cooperation. Enter your phone number.",
                                   reply_markup=get_remove_keyboard_markup())
            bot.register_next_step_handler(msg, get_phone_number_en)

        else:
            msg = bot.send_message(chat_id, "Please choose visit reason.",
                                   reply_markup=get_visit_reason_markup_en())
            bot.register_next_step_handler(msg, get_visit_reason_en)

    except Exception as err:
        print(err)


def get_visit_reason_markup_en():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('familiarization')
    itembtn2 = types.KeyboardButton('cooperation')
    markup.add(itembtn1, itembtn2)
    return markup


def get_remove_keyboard_markup():
    markup = types.ReplyKeyboardRemove(selective=False)
    return markup


def get_phone_number_ru(message):
    global number

    phone_number = message.text.strip()
    number = phone_number

    message.phone_number = phone_number
    chat_id = message.chat.id
    user_data[chat_id] = {'phone_number': phone_number,
                          'email': None
                          }

    bot.reply_to(message, f"Спасибо, я получил ваш номер телефона: {phone_number}!")

    bot.reply_to(message, "Введите ваш адрес электронной почты.")
    bot.register_next_step_handler(message, get_email_ru)


def get_phone_number_ro(message):
    global number

    phone_number = message.text.strip()
    number = phone_number

    message.phone_number = phone_number
    chat_id = message.chat.id
    user_data[chat_id] = {
        'phone_number': phone_number,
        'email': None
    }

    bot.reply_to(message, f"Multumesc, eu primit numarul de telefon: {phone_number}!")

    bot.reply_to(message, "Introduceti adresa email")
    bot.register_next_step_handler(message, get_email_ro)


def get_phone_number_en(message):
    global number

    phone_number = message.text.strip()
    number = phone_number

    message.phone_number = phone_number
    chat_id = message.chat.id
    user_data[chat_id] = {'phone_number': phone_number,
                          'email': None
                          }

    bot.reply_to(message, f"I received your phone number: {phone_number}!")

    bot.reply_to(message, "Enter your email address.")
    bot.register_next_step_handler(message, get_email_en)


def get_email_ru(message):
    global mail

    email = message.text.strip()
    mail = email
    chat_id = message.chat.id
    user_data[chat_id]['email'] = email
    bot.reply_to(message, f"Спасибо, я получил ваш адрес электронной почты: {email}! "
                          "Благодарим за предоставленные данные, мы свяжемся с вами в ближайшее время.")
    bot.register_next_step_handler(main())


def get_email_ro(message):
    global mail

    email = message.text.strip()
    mail = email
    chat_id = message.chat.id
    user_data[chat_id]['email'] = email
    bot.reply_to(message, f"multumesc am primit adresa ta de email: {email}! "
                          "multumim pentru informatiile oferite, va vom contacta in cel mai scurt timp posibil.")
    bot.register_next_step_handler(main())


def get_email_en(message):
    global mail

    email = message.text.strip()
    mail = email
    chat_id = message.chat.id
    user_data[chat_id]['email'] = email
    bot.reply_to(message, f"Thanks, i received your email address: {email}! "
                          "Thank you for the information provided, we will contact you as soon as possible.")
    bot.register_next_step_handler(main())


while True:

    try:

        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
