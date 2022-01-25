from telebot import types
from functions import *
from bot import bot, db
from config import OWM_key


@bot.message_handler(commands=['start'])  # Команда /start
def start(message):
    if not db.user_exist('records', message.chat.id):
        bot.send_message(message.chat.id, 'Введите название вашего населенного пункта')
        bot.register_next_step_handler(message, start_user_city)
    else:
        bot.send_message(message.chat.id, 'Вы уже зарегистрировались')


def start_user_city(message):     # Добавить юзера в таблицу records
    if get_weather(message.text, OWM_key):
        db.add_user(message.chat.id)
        db.add_notice(message.chat.id, message.text.lower())
        bot.send_message(message.chat.id, 'Теперь вы можете настроить уведомление. По умолчанию стоит 6:00 по московскому времени')
        send_keyboard(message)
    else:
        bot.send_message(message.chat.id, 'Не подходящий населенный пункт')
        bot.register_next_step_handler(message, start_user_city)


@bot.message_handler(commands=['help'])  # Команда /help
def help(message):
    pass


@bot.message_handler(content_types=['text'])  # Обработчик текста
def text_detector(message):
    text = message.text.lower()
    if text == 'какая погода в':
        bot.send_message(message.chat.id, 'Введите название города', reply_markup=back_keyboard)
        bot.register_next_step_handler(message, weather)
    elif text == 'настроить уведомление':
        res = db.get_user_info(message.chat.id)
        bot.send_message(message.chat.id, f"Город: {res['city']}\nВремя: {res['time']}\nУведомление: {'Включено' if int(res['notice']) else 'Выключено'}", reply_markup=notice_keyboard)
        bot.register_next_step_handler(message, settings_notice, res)
    else:
        send_keyboard(message)


def weather(message):  # Присылает погоду
    text = message.text
    if text.lower() != 'отмена':
        w = get_weather(text, OWM_key)
        if w:
            bot.send_message(message.chat.id, w)
        else:
            bot.send_message(message.chat.id, 'Проверьте правильно ли вы написали название города')
        bot.register_next_step_handler(message, weather)
    else:
        send_keyboard(message)


def settings_notice(message, res):  # Редактирует уведомление
    text = message.text.lower()
    if text != 'отмена':
        if text == 'вкл':
            if res['notice'] == 0:
                db.notice_update(message.chat.id, ('notice', 1))
        elif text == 'выкл':
            if res['notice'] == 1:
                db.notice_update(message.chat.id, ('notice', 0))
        elif text == 'город':
            bot.send_message(message.chat.id, 'Укажите ближайший населенный пункт', reply_markup=back_keyboard)
            bot.register_next_step_handler(message, set_city, res)
            return
        elif text == 'время':
            pass
        res = db.get_user_info(message.chat.id)
        bot.send_message(message.chat.id, f"Город: {res['city']}\nВремя: {res['time']}\nУведомление: {'Включено' if int(res['notice']) else 'Выключено'}")
        bot.register_next_step_handler(message, settings_notice, res)
    else:
        send_keyboard(message)


def set_city(message, res):
    text = message.text.lower()
    if text != 'отмена':
        if res['city'] != text:
            if get_weather(text, OWM_key):
                db.notice_update(message.chat.id, ('city', text))
                res['city'] = text
                bot.send_message(message.chat.id, f"Город: {res['city']}\nВремя: {res['time']}\nУведомление: {'Включено' if int(res['notice']) else 'Выключено'}", reply_markup=notice_keyboard)
                bot.register_next_step_handler(message, settings_notice, res)
                return
        bot.send_message(message.chat.id, 'Не подходящий населенный пункт')
        bot.register_next_step_handler(message, set_city, res)
    else:
        bot.register_next_step_handler(message, settings_notice, res)


def send_keyboard(message):     # Присылает юзеру клавиатуру
    bot.send_message(message.chat.id, 'Вот что я умею', reply_markup=main_keyboard)


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
