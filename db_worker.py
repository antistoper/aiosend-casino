import sqlite3

class DBINIT:
    def __init__(self, filename):
        """Инициализация бота"""
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def delete_new_column(self):
        self.cursor.execute("alter table users drop column money")
        self.cursor.execute("alter table users drop column referals")
        self.cursor.execute("alter table users drop column referer")
        self.connection.commit()

    def migrate(self):
        try:
            self.cursor.execute("alter table users add column balance")
            self.connection.commit()
        except sqlite3.OperationalError:
            return 
    
    def get_balance(self, user_id):
        with self.connection:
            res = self.cursor.execute(f"""SELECT balance FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_balance(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET balance={nums} WHERE id={user_id}""")
            self.connection.commit()

    def get_all_maxbet(self):
        with self.connection:
            res = self.cursor.execute(f"""SELECT * FROM maxbet WHERE const=1""").fetchall()
            return res[0]

    def set_all_maxbet(self, nums, user_id, name):
        with self.connection:
            self.cursor.execute(f"""UPDATE maxbet SET bet={nums}, USER_ID={user_id}, NAME="{name}" WHERE const=1""")
            self.connection.commit()

    def get_win(self, user_id):
        with self.connection:
            res = self.cursor.execute(f"""SELECT wins FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_win(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET wins={nums} WHERE id={user_id}""")
            self.connection.commit()

    def get_lose(self, user_id):
        with self.connection:
            res = self.cursor.execute(f"""SELECT loses FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_lose(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET loses={nums} WHERE id={user_id}""")
            self.connection.commit() 

    def get_biggest_stake(self, user_id):
        """Получить самую большую ставку"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT biggest_stake FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_biggest_stake(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET biggest_stake={nums} WHERE id={user_id}""")
            self.connection.commit()

    def get_maxwin(self, user_id):
        with self.connection:
            res = self.cursor.execute(f"""SELECT maxwin FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_maxwin(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET maxwin={nums} WHERE id={user_id}""")
            self.connection.commit()

    def get_oborot(self, user_id):
        with self.connection:
            res = self.cursor.execute(f"""SELECT oborot_total FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_oborot(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET oborot_total={nums} WHERE id={user_id}""")
            self.connection.commit()   

    def get_oborot_month(self, user_id):
        with self.connection:
            res = self.cursor.execute(f"""SELECT oborot_month FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]

    def set_oborot_month(self, user_id, nums):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET oborot_month={nums} WHERE id={user_id}""")
            self.connection.commit()   

    def users_exists(self, user_id):
        """Проверка на юзера"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT * FROM users WHERE id={user_id}""").fetchall()
            return bool(len(res))

    def add_user(self, user_id, referer):
        """Добавляем юзера с начальным значением biggest_stake = 0"""
        with self.connection:
            self.cursor.execute(
                """INSERT INTO users (id, wins, loses, active, total, moneyback, referer, biggest_stake, maxwin, oborot_total, oborot_month, referals)
                VALUES (?, 0, 0, 1, 0, 0, ?, 0, 0, 0, 0, 0)""",
                (user_id, referer)
            )
            self.connection.commit()
        
    def get_active_users(self):
        """Получаем всех активных юзеров"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT id FROM users WHERE active=1""").fetchall()
            return res
    
    def get_users(self):
        """Получаем всех юзеров"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT id FROM users""").fetchall()
            return res
        
    def get_total(self, user_id):
        """Получить всего ставок"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT total FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]
        
    def edit_total(self, user_id, amount):
        """Обновить тотал"""
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET total={self.get_total(user_id) + amount} WHERE id={user_id}""")
            self.connection.commit()

    def get_moneyback(self, user_id):
        """Получить манибек"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT moneyback FROM users WHERE id={user_id}""").fetchall()
            return res[0][0]
        
    def edit_moneyback(self, user_id, amount):
        """Редачить манибэк"""
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET moneyback={self.get_moneyback(user_id) + amount} WHERE id={user_id}""")
            self.connection.commit()

    def set_active(self, user_id, status = 1):
        """Установить актив"""
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET active={status} WHERE id={user_id}""")
            self.connection.commit()

    def add_check(self, user_id, check_id):
        """Добавить чек"""
        with self.connection:
            self.cursor.execute(f"""INSERT INTO checks VALUES ({user_id}, {check_id}) """)
            self.connection.commit()

    def have_check(self, user_id):
        """Поиметь чек ой тоесть проверка на наличие"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT * FROM checks WHERE user_id={user_id}""").fetchall()
            return bool(len(res))
        
    def check_exists(self, check_id):
        """Сущетсвует ли чек с таким айди"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT * FROM checks WHERE check_id={check_id}""").fetchall()
            return bool(len(res))
        
    def remove_check(self, check_id):
        """Удалить чек"""
        with self.connection:
            self.cursor.execute(f"""DELETE FROM checks WHERE check_id={check_id} """)
            self.connection.commit()
    
    def get_check_id(self, user_id):
        """Получить айди чека"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT check_id FROM checks WHERE user_id={user_id}""").fetchone()
            return res[0]
        
    def get_checks(self):
        """Получить все чеки"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT check_id FROM checks""")
            ids=[]
            for r in res:
                ids.append(r[0])
            return ids
    
    def ban_user(self, user_id):
        """Забанить юзера"""
        with self.connection:
            self.cursor.execute(f"""INSERT INTO banned VALUES ({user_id})""")
            self.connection.commit()
    
    def deban_user(self, user_id):
        """Разбанить юзера"""
        with self.connection:
            self.cursor.execute(f"""DELETE FROM banned WHERE id={user_id} """)
            self.connection.commit()
    
    def get_bannned(self) -> list:
        """Получить список забаненых"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT id FROM banned""").fetchall()
            ids = []
            if len(res) > 0: 
                for r in res:
                    ids.append(r[0])
            return ids
    
    def add_mines(self, user_id, bad_mines, amount, asset, username):
        """Добавить мины. Крч, создать игру в бд."""
        with self.connection:
            self.cursor.execute(f"""INSERT INTO mines VALUES ({user_id}, "{str(bad_mines)}", {amount}, "{asset}", "{username}")""")
            self.connection.commit()
    
    def mines_exist(self, user_id) -> bool:
        return bool(len(self.cursor.execute(f"""SELECT * FROM mines WHERE id={user_id}""").fetchall()))

    def get_data_mines(self, user_id) -> dict:
        """Получить сумму валюту и юз чела из мин"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT amount, asset, username FROM mines WHERE id={user_id}""").fetchall()
            return {"amount": res[0][0], "asset": res[0][1], "username": res[0][2]}
        
    def get_bad_mines(self, user_id):
        """Получить корды мин"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT bad FROM mines WHERE id={user_id}""").fetchall()
            return eval(res[0][0])
    
    def user_played_mines(self, user_id):
        """Проверка на то, играет ли игрок в мину"""
        with self.connection:
            res = self.cursor.execute(f"""SELECT * FROM mines WHERE id={user_id}""").fetchall()
            return bool(len(res))
    
    def remove_mines(self, user_id):
        """Удалить игру из бд"""
        with self.connection:
            self.cursor.execute(f"""DELETE FROM mines WHERE id={user_id} """)
            self.connection.commit()
    
    def set_money(self, user_id, amount):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET money={amount} WHERE id={user_id}""")
            self.connection.commit()

    def set_referals(self, user_id, amount):
        with self.connection:
            self.cursor.execute(f"""UPDATE users SET referals={amount} WHERE id={user_id}""")
            self.connection.commit()
    
    def get_money(self, user_id):
        with self.connection:
            return self.cursor.execute(f"""SELECT money FROM users WHERE id={user_id}""").fetchall()[0][0]

    def get_referals(self, user_id):
        with self.connection:
            return self.cursor.execute(f"""SELECT referals FROM users WHERE id={user_id}""").fetchall()[0][0]

    def get_referer(self, user_id):
        with self.connection:
            return self.cursor.execute(f"""SELECT referer FROM users WHERE id={user_id}""").fetchall()[0][0]
            