from telebot import types
import telebot
import sqliter
import config
from functions import *


db = sqliter.sqliter('../database.db')
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])  # Команда /start
def start(message):
    bot.send_message(message.chat.id, 'Помогу узнать погоду в любом городе.', reply_markup=main_keyboard)
    db.add_user(message.chat.id)


@bot.message_handler(commands=['help'])  # Команда /help
def send_help(message):
    bot.send_message(message.chat.id, 'Управляйте ботом с помощью кнопок!')


@bot.message_handler(content_types=['text'])  # Обработчик текста
def text_detector(message):
    text = message.text.lower()
    if text == 'какая погода в':
        mes_id = bot.send_message(message.chat.id, 'Введите название города', reply_markup=back_keyboard).message_id
        bot.register_next_step_handler(message, weather)
    elif text == 'настроить уведомление':
        bot.send_message(message.chat.id, 'Изменение уведомления', reply_markup=notice_keyboard)
        bot.register_next_step_handler(message, settings_notice)
    else:
        bot.send_message(message.chat.id, 'Если что то не понятно пиши /help')


def weather(message):  # Присылает погоду
    text = message.text
    if text.lower() != 'отмена':
        w = get_weather(text, config.OWM_key)
        if w:
            bot.send_message(message.chat.id, w)
        else:
            bot.send_message(message.chat.id, 'Проверьте правильно ли вы написали название города')
        bot.register_next_step_handler(message, weather)
    else:
        bot.send_message(message.chat.id, 'ЭЙ УЗНАЛ ПОГОДУ ДРУГИМ НЕ МАШАЙ', reply_markup=main_keyboard)


def add_subscribe(message):
    bot.send_message(message.chat.id, 'Введите название города', reply_markup=back_keyboard)
    city = bot.register_next_step_handler(subscribe_step1(message, config.OWM_key))
    if city:
        pass


def settings_notice(message):  # Редактирует уведомление
    text = message.text.lower()
    if text != 'отмена':
        if text == 'вкл':
            pass
        elif text == 'выкл':
            pass
        elif text == 'город':
            pass
        elif text == 'время':
            pass
        bot.register_next_step_handler(message, settings_notice)
    else:
        bot.send_message(message.chat.id, 'бебебе', reply_markup=main_keyboard)


def create_keyboard(*args):  # Создает markup клавиатуру
    markup = types.ReplyKeyboardMarkup()
    for i in args:
        if type(i) == list:
            markup.row(*[types.KeyboardButton(x) for x in i])
            continue
        markup.row(types.KeyboardButton(i))
    return markup


main_keyboard = create_keyboard('Какая погода в', 'Настроить уведомление')
notice_keyboard = create_keyboard(['Вкл', 'Выкл'], ['Город', 'Время'], 'Отмена')
back_keyboard = create_keyboard('Отмена')

if __name__ == '__main__':
    bot.infinity_polling()
