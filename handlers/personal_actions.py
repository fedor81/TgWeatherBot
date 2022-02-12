from telebot import types
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from functions import get_weather
from bot import bot, db
from config import OWM_key


fmt = '%H:%M'
moscow = timezone('Europe/Moscow')


@bot.message_handler(commands=['start'])  # Команда /start
def start(message):
    if not db.user_exist('users', message.chat.id):
        bot.send_message(message.chat.id, 'Введите название вашего населенного пункта')
        bot.register_next_step_handler(message, start_user_city)
    else:
        bot.send_message(message.chat.id, 'Вы уже зарегистрировались')


def start_user_city(message):     # определение города
    text = get_weather(message.text, OWM_key, True)
    if text:
        local_time, server_time = get_city_zone(text, 8, 0)
        db.add_user(message.chat.id)
        db.add_notice(message.chat.id, text, server_time, local_time)
        send_keyboard(message)
    else:
        bot.send_message(message.chat.id, 'Не подходящий населенный пункт')
        bot.register_next_step_handler(message, start_user_city)


def get_city_zone(city, hour, minute):      # Переводчик время в Московское
    chance = 0
    ci = None

    for i in pytz.all_timezones:
        try:
            chan = db.tanimoto(i.split('/')[1], city)
            if chan > chance:
                chance = chan
                ci = i
        except IndexError:
            pass

    local_time = datetime.now(timezone(ci)).replace(hour=hour, minute=minute)
    server_time = local_time.astimezone(moscow)
    return local_time.strftime(fmt), server_time.strftime(fmt)


@bot.message_handler(commands=['help'])  # Команда /help
def message_help(message):
    pass


@bot.message_handler(content_types=['text'])  # Обработчик текста
def text_detector(message):
    text = message.text.lower()
    if text == 'какая погода в':
        bot.send_message(message.chat.id, 'Введите название города', reply_markup=back_keyboard)
        bot.register_next_step_handler(message, weather)
    elif text == 'настроить уведомление':
        res = db.get_user_info(message.chat.id)
        send_settings(message, res, notice_keyboard)
        bot.register_next_step_handler(message, settings_notice, res)
    elif text == 'погода сейчас':
        w = get_weather(db.get_user_info(message.chat.id)['city'], OWM_key)
        bot.send_message(message.chat.id, w)
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
            bot.send_message(message.chat.id, 'Ведите время в формате часы:минуты.\nНапример: 8:00', reply_markup=back_keyboard)
            bot.register_next_step_handler(message, set_time, res)
            return
        res = db.get_user_info(message.chat.id)
        send_settings(message, res, None)
        bot.register_next_step_handler(message, settings_notice, res)
    else:
        send_keyboard(message)


def set_city(message, res):
    text = message.text.lower()
    if text != 'отмена':
        if res['city'] != text:
            city = get_weather(text, OWM_key, True)
            if city:
                local_time, server_time = get_city_zone(city, *list(map(int, res['local_time'].split(':'))))
                db.notice_update(message.chat.id, ('city', city))
                db.notice_update(message.chat.id, ('server_time', server_time))
                res['city'], res['server_time'] = city, server_time
                send_settings(message, res, notice_keyboard)
                bot.register_next_step_handler(message, settings_notice, res)
                return
        bot.send_message(message.chat.id, 'Не подходящий населенный пункт')
        bot.register_next_step_handler(message, set_city, res)
    else:
        send_settings(message, res, notice_keyboard)
        bot.register_next_step_handler(message, settings_notice, res)


def set_time(message, res):
    text = message.text.lower()
    if text != 'отмена':
        try:
            new_time = list(map(int, text.split(':')))
            last_time = list(map(int, res['local_time'].split(':')))
            if new_time != last_time:
                if new_time[0] < 24 and new_time[1] < 60:
                    local_time, server_time = get_city_zone(res['city'], *new_time)
                    db.notice_update(message.chat.id, ('server_time', server_time))
                    db.notice_update(message.chat.id, ('local_time', local_time))
                    res['local_time'], res['server_time'] = local_time, server_time
                    send_settings(message, res, notice_keyboard)
                    bot.register_next_step_handler(message, settings_notice, res)
                    return
        except:
            pass
        bot.send_message(message.chat.id, 'Не подходящее время')
        bot.register_next_step_handler(message, res)
    else:
        send_settings(message, res, notice_keyboard)
        bot.register_next_step_handler(message, settings_notice, res)


def send_keyboard(message):     # Присылает юзеру клавиатуру
    bot.send_message(message.chat.id, 'Вот что я умею', reply_markup=main_keyboard)


def send_settings(message, res, markup):       # Присылает настройки уведомления
    bot.send_message(message.chat.id, f"Город: {res['city']}\nВремя: {res['local_time']}\nУведомление: {'Включено' if int(res['notice']) else 'Выключено'}", reply_markup=markup)


def create_keyboard(*args):  # Создает markup клавиатуру
    markup = types.ReplyKeyboardMarkup()
    for i in args:
        if type(i) == list:
            markup.row(*[types.KeyboardButton(x) for x in i])
            continue
        markup.row(types.KeyboardButton(i))
    return markup


main_keyboard = create_keyboard(['Погода сейчас', 'Какая погода в'], 'Настроить уведомление')
notice_keyboard = create_keyboard(['Вкл', 'Выкл'], ['Город', 'Время'], 'Отмена')
back_keyboard = create_keyboard('Отмена')


if __name__ == '__main__':
    bot.infinity_polling()