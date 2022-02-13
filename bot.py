from sqliter import sqliter
from config import TOKEN
import telebot
import handlers

db = sqliter('database.db')
bot = telebot.TeleBot(TOKEN)

if __name__ == '__main__':
    handlers.main()