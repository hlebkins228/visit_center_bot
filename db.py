import psycopg2
from psycopg2 import DatabaseError
from datetime import datetime

from logger import logger_client
from exeptions import *
from config import DATE_FORMAT
from config import DB_NAME, DB_LOGIN, DB_PASSWORD, DB_PORT, DB_HOST
from config import MIN_ORDER_ID, MAX_ORDER_ID
from typing import TypedDict
from datetime import datetime
from random import randint
import pandas as pd


class UserRecord(TypedDict):
    id: int
    user_id: int
    username: str
    name: str
    reg_date: datetime

class OrderRecord(TypedDict):
    id: int
    order_id: int
    user_id: int
    service_id: str
    order_date: datetime

class ContactRecord(TypedDict):
    id: int
    user_id: int
    first_name: str
    last_name: str
    phone: str

class UserInfo(TypedDict):
    user_data: UserRecord
    contact_data: ContactRecord | None


class DBClient:
    def __init__(self, user: str = 'login', password: str = 'password', host: str = 'localhost', port: str = '5432', db_name: str = 'example') -> None:
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.conn = None
        self.cursor = None

        self.logger = logger_client

        self.connect_db()
    
    def connect_db(self) -> None:
        try:
            self.conn = psycopg2.connect(database=self.db_name, user=self.user, password=self.password, host=self.host,
                                         port=self.port)
        except DatabaseError as e:
            self.logger.error_exp(e)
        else:
            self.cursor = self.conn.cursor()
        
    def close_connection(self) -> None:
        self.cursor.close()
        self.conn.close()
    
    def is_connected(self) -> None:
        if self.cursor is None or self.conn is None:
            raise NoDBConnectionError()
    
    def is_user_exist(self, user_id: str) -> bool:
        self.cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id, ))
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def add_user(self, user_id: int, username: str, name: str) -> None:
        self.is_connected()

        if self.is_user_exist(user_id):
            raise UserAlreadyExist()
        
        self.cursor.execute(f'''INSERT INTO users (user_id, username, name, reg_date) VALUES
                            ({user_id},
                            '{username}',
                            '{name}',
                            '{datetime.now().strftime(DATE_FORMAT)}')''')
    
        self.conn.commit()

    def get_user(self, user_id: int) -> UserRecord | None:
        self.is_connected()

        self.cursor.execute("SELECT id, user_id, username, name, reg_date FROM users WHERE user_id = %s", (user_id, ))
        
        result = self.cursor.fetchone()
        if result:
            return UserRecord(id=int(result[0]), user_id=result[1], username=result[2], name=result[3], reg_date=datetime.strftime(result[4], DATE_FORMAT))
        else:
            return None
    
    def change_name(self, user_id: int, new_name: str) -> None:
        self.is_connected()
        
        self.cursor.execute("UPDATE users SET name = %s WHERE user_id = %s", (new_name, user_id))

        self.conn.commit()
    
    def get_all_users_id(self) -> list[int]:
        self.is_connected()

        self.cursor.execute("SELECT user_id FROM users")

        result = self.cursor.fetchall()
        if result:
            return [int(row[0]) for row in result]
        else:
            return []

    def is_admin_exist(self, username: str) -> bool:
        self.cursor.execute("SELECT 1 FROM admins WHERE username = %s", (username, ))
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def add_admin(self, username: str) -> None:
        self.is_connected()

        if self.is_admin_exist(username):
            raise UserAlreadyExist("admin with such username already exists")
        
        self.cursor.execute("INSERT INTO admins (username) VALUES (%s)", (username, ))
        self.conn.commit()
    
    def change_admin_user_id(self, username: str, user_id: int) -> None:
        self.is_connected()

        if self.is_admin_exist(username):
            self.cursor.execute("UPDATE admins SET user_id = %s WHERE username = %s", (user_id, username))

        self.conn.commit()
    
    def del_admin(self, username: str) -> None:
        self.is_connected()

        if not self.is_admin_exist(username):
            raise UserNotExist("admin with such username does not exist in database")

        self.cursor.execute("DELETE FROM admins WHERE username = %s", (username, ))
        self.conn.commit()

    def get_all_admins_id(self) -> list[int]:
        self.is_connected()

        self.cursor.execute("SELECT u.user_id FROM users u JOIN admins a ON u.username = a.username")

        result = self.cursor.fetchall()
        if result:
            return [int(row[0]) for row in result]
        else:
            return []
    
    def get_all_admins_username(self) -> list[str]:
        self.is_connected()

        self.cursor.execute("SELECT username FROM admins")

        result = self.cursor.fetchall()
        if result:
            return [str(row[0]).strip() for row in result]
        else:
            return []
    
    def gen_order_id(self) -> int:
        self.cursor.execute("SELECT order_id FROM orders")
        
        orders_id = list()
        result = self.cursor.fetchall()
        if not (result is None):
            for order in result:
                orders_id.append(int(order[0]))
        
        while True:
            new_id = randint(MIN_ORDER_ID, MAX_ORDER_ID)
            if new_id not in orders_id:
                return new_id

    # Записываем user_id и id услуги которую он заказал.
    # Также сохнаряем timestamp. Поля имя, фамилия, телефон сделать не обязательными, они добавляются через add_user_contact_data в случае если пользователь нажал кнопку поделиться контактом
    def add_user_order_data(self, user_id: int, service_id: int) -> None:
        self.is_connected()

        self.cursor.execute("INSERT INTO orders (order_id, user_id, service_id, order_date) VALUES (%s, %s, %s, %s)", (self.gen_order_id(), user_id, service_id, datetime.now().strftime(DATE_FORMAT)))
        self.conn.commit()
    
    # в данном случае поле id может быть любым
    def add_user_order_record(self, order: OrderRecord) -> None:
        self.is_connected()

        self.cursor.execute("INSERT INTO orders (order_id, user_id, service_id, order_date) VALUES (%s, %s, %s, %s)", (order['order_id'], order['user_id'], order['service_id'], order['order_date']))
        self.conn.commit()

    def get_user_orders_data(self, user_id: int) -> list[OrderRecord] | None:
        self.cursor.execute("SELECT id, user_id, service_id, order_date FROM orders WHERE user_id = %s", (user_id, ))
        
        orders_list = list()
        result = self.cursor.fetchall()
        if result is None:
            return None
        for order in result:
            orders_list.append(OrderRecord(id=int(order[0]), user_id=int(order[1]), service_id=int(order[2]), order_date=datetime.strftime(order[3], DATE_FORMAT)))
        
        return orders_list
        
    def is_user_contact_data_exist(self, user_id: int) -> bool:
        self.cursor.execute("SELECT 1 FROM contacts WHERE user_id = %s", (user_id, ))
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def add_user_contact_data(self, user_id: int, first_name: str, last_name: str, phone: str) -> None:
        self.is_connected()
        if self.is_user_contact_data_exist(user_id):
            raise UserAlreadyExist("User contact data already exists")

        self.cursor.execute("INSERT INTO contacts (user_id, first_name, last_name, phone) VALUES (%s, %s, %s, %s)", (user_id, first_name, last_name, phone))
        self.conn.commit()
    
    def get_user_contact_data(self, user_id: int) -> ContactRecord | None:
        self.cursor.execute("SELECT id, user_id, first_name, last_name, phone FROM contacts WHERE user_id = %s", (user_id, ))
        
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        contact = ContactRecord(id=int(result[0]), user_id=int(result[1]), first_name=result[2], last_name=result[3], phone=result[4])
        return contact

    def get_user_info(self, user_id: int) -> UserInfo:
        user_data = self.get_user(user_id)
        if user_data is None:
            return None
        contact_data = self.get_user_contact_data(user_id)

        return UserInfo(user_data=user_data, contact_data=contact_data)

    def get_all_users_info(self) -> list[UserInfo]:
        data = list()
        for user_id in self.get_all_users_id():
            data.append(self.get_user_info(user_id))
        
        return data


def write_data_to_csv(data: list[UserInfo], file_path: str) -> None:
    formated_data = {
        "id": [],
        "user_id": [],
        "alias": [],
        "reg_date": [],
        "first_name": [],
        "last_name": [],
        "phone": []
    }

    for user in data:
        formated_data["id"].append(user["user_data"]["id"])
        formated_data["user_id"].append(user["user_data"]['user_id'])
        formated_data["alias"].append(user["user_data"]["name"])
        formated_data["reg_date"].append(user["user_data"]["reg_date"])
        formated_data["first_name"].append(user["contact_data"]["first_name"] if user["contact_data"] is not None else "None")
        formated_data["last_name"].append(user["contact_data"]["last_name"] if user["contact_data"] is not None else "None")
        formated_data["phone"].append(user["contact_data"]["phone"] if user["contact_data"] is not None else "None")

    csv_data = pd.DataFrame(formated_data)
    csv_data.to_csv(file_path, index=False, sep=';', encoding='utf-8')


db_client = DBClient(db_name=DB_NAME, user=DB_LOGIN, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

write_data_to_csv(db_client.get_all_users_info(), "test.csv")


