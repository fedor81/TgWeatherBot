from sqliter import sqliter
from config import TOKEN
import telebot

db = sqliter('database.db')
bot = telebot.TeleBot(TOKEN)

if __name__ == '__main__':
    bot.infinity_polling()