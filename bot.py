from config import bot
from sqliter import sqliter


db = sqliter('database.db')


if __name__ == '__main__':
    bot.polling()