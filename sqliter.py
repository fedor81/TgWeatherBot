import sqlite3


class sqliter:

    def __init__(self, db_file):    # Иницилизация БД
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def add_user(self, id):     # Добавление юзера в БД по его id
        if not self.user_exist('users', id):
            self.cursor.execute("INSERT INTO users (id) VALUES (?)", (id,))
            self.conn.commit()

    def user_exist(self, table, id):   # Проверка есть ли юзер в БД
        result = self.cursor.execute(f"SELECT id FROM {table} WHERE id = (?)", (id,))
        return bool(len(result.fetchall()))

    def add_notice(self, id, city, time):
        self.cursor.execute("INSERT INTO records (id, notice, city, msc_time) VALUES (?, ?, ?, ?)", (id, 1, city, time))
        self.conn.commit()

    def notice_update(self, id, **args):      # Принимает id и словарь
        for i in args.keys():
            pass

    def get_user_info(self, id, *args):
        pass

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    a = sqliter('database.db')