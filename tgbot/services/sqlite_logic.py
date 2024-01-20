# - *- coding: utf- 8 - *-
import math
import random
import sqlite3

from tgbot.data.config import PATH_DATABASE, PATH_PROMOCODE
from tgbot.utils.const_functions import get_unix, get_date, clear_html


# Получение данных о товарах
def get_all_item():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute("SELECT position_name, position_id, position_price  FROM storage_position").fetchall()
        records = []
        current_positions = 1
        for row in data:
            character = dict()
            character['position'] = current_positions
            character['name_item'] = row[0]
            character['id_item'] = row[1]
            character['price'] = row[2]
            records.append(character)
            current_positions += 1
        return records
#Получение данных о предзаказов
def get_all_preorder():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute("SELECT user_id, username, item_position_name, item_position_id, count FROM storage_pre_order").fetchall()
        records = []
        current_positions = 1
        for row in data:
            character = dict()
            character['position'] = current_positions
            character['user_id'] = row[0]
            character['username'] = row[1]
            character['item_position_name'] = row[2]
            character['item_position_id'] = row[3]
            character['count'] = row[4]
            records.append(character)
            current_positions += 1
        return records


# Получение данных о промокодаъ
def get_all_promocode():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute("SELECT promocode, item_position_name, item_position_id, discount FROM storage_promocode").fetchall()
        records = []
        current_positions = 1
        for row in data:
            character = dict()
            character['position'] = current_positions
            character['name_promocode'] = row[0]
            character['name_item'] = row[1]
            character['item_position_id'] = row[2]
            character['discount'] = row[3]
            records.append(character)
            current_positions += 1
        return records


#Проверка, есть ль совпадающие промокоды
def check_promocode(promocode):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute("SELECT promocode FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchall()
        return len(data)

def add_promocode(promocode, user_id, name_item, id_item, discount, use_count, one_use, all_items):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute("INSERT INTO storage_promocode "
                "(promocode, user_id, item_position_id, item_position_name, all_items, discount, use_count, one_use)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [promocode, user_id, id_item, name_item , all_items, discount, use_count, one_use])
        con.commit()
        promocode_id = con.execute(f"SELECT promocode_id FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        if one_use ==  True: #Если промокод является единоразовым, то создать таблицу с названием промокода
            with sqlite3.connect(PATH_PROMOCODE) as com:
                com.execute(f"CREATE TABLE promocode_{str(promocode_id)}("
                  "user_id INTEGER,"
                  "use INT)", )
            com.commit()
def check_promocode(promocode):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute("SELECT * FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchall()
        return data


def check_use_promocode(promocode):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT use_count FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        return data

def used_promocode(promocode, user_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        promocode_id = con.execute(f"SELECT promocode_id FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        try: #Промокод единораз
            with sqlite3.connect(PATH_PROMOCODE) as com:
                user = com.execute(f"SELECT use FROM  promocode_{str(promocode_id)}  WHERE user_id = ?", (user_id,)).fetchone()
                if user == None:
                    return 0
                elif user[0] == 0:
                    return  1
        except:
            pass


def update_promocode(promocode, user_id):
    try:
        with sqlite3.connect(PATH_DATABASE) as con:
            promocode_id = con.execute(f"SELECT promocode_id FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
            with sqlite3.connect(PATH_PROMOCODE) as com:
                user = com.execute(f"SELECT use FROM  promocode_{str(promocode_id)}  WHERE user_id = ?", (user_id,)).fetchone()
                if user == None:
                    com.execute(f"INSERT INTO promocode_{str(promocode_id)}(user_id, use) VALUES (?, ?)", [user_id, 0])
                    return 0

                elif user[0] == 0:
                    com.execute(f"UPDATE  promocode_{str(promocode_id)} SET use = ? WHERE user_id = ?", (1, user_id))
                    return  1
    except:
        pass

    finally:
        data = con.execute(f"SELECT use_count FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        con.execute(f"UPDATE storage_promocode SET use_count = ? WHERE promocode = ?", ((data - 1), promocode))


def get_id_promocode(promocode):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT promocode_id FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        return data

def get_promocode(id_procomode):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT promocode FROM storage_promocode  WHERE promocode_id = ?", (id_procomode,)).fetchone()[0]
        return data


def used_pre_order(user_id, username, position_id, position_name, count):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute("INSERT INTO storage_pre_order "
                "(user_id, username, item_position_id, item_position_name, count)"
                "VALUES (?, ?, ?, ?, ?)",
                [user_id, username, position_id, position_name , count])
        con.commit()

def get_info(promocode, category):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT {category} FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        return data



def update_info_discount_count_use(promocode, category, data):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_promocode SET {category} = ? WHERE promocode = ?", (data, promocode))
        return True

def update_info_items_promocode(promocode, item_name, item_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_promocode SET (item_position_id, item_position_name, all_items) = (?, ?, ?) WHERE promocode = ?", (item_id, item_name, 0, promocode))
        return True

def update_info_all_items_promocode(promocode):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_promocode SET (item_position_id, item_position_name, all_items) = (?, ?, ?) WHERE promocode = ? ", (None, None, 1, promocode))
        promocode_id = con.execute(f"SELECT promocode_id FROM storage_promocode  WHERE promocode = ?", (promocode,)).fetchone()[0]
        con.commit()
    with sqlite3.connect(PATH_PROMOCODE) as com:
        com.execute(f"CREATE TABLE IF NOT EXISTS promocode_{str(promocode_id)}("
                    "user_id INTEGER,"
                    "use INT)")
        com.commit()
        return True

def delete_pre_order(user_id, position_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute("DELETE FROM storage_pre_order WHERE user_id = ? AND item_position_id = ?", (user_id, position_id) )

def get_len_items(position_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT item_id, item_data FROM storage_item  WHERE position_id = ?", (position_id,)).fetchall()
        return data



def update_pre_order_(position_id, user_id, count, item_id):
    try:
        with sqlite3.connect(PATH_DATABASE) as con:
            data = con.execute(f"SELECT count FROM storage_pre_order  WHERE user_id = ? and item_position_id = ?", (user_id, position_id)).fetchone()[0]
            data_count = data - count
            if data_count <= 0:
                con.execute("DELETE FROM storage_pre_order WHERE user_id = ? AND item_position_id = ?",  (user_id, position_id))
            else:
                con.execute( f"UPDATE storage_pre_order SET count = ? WHERE user_id = ? and item_position_id = ?", (data_count, user_id, position_id))
    except:
        pass
    finally:
        for i in range(count):
            con.execute("DELETE FROM storage_item WHERE position_id = ? AND item_id = ?", (position_id, item_id))
        con.commit()


def check_preorder(position_id, user_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT count FROM storage_pre_order  WHERE item_position_id = ? and user_id = ?", (position_id, user_id)).fetchone()
        try:
            if data[0] == 0:
                return False
            else:
                return True
        except TypeError:
            return True

def get_preoder(position_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT position_pre_order FROM storage_position  WHERE position_id = ?", (position_id,)).fetchone()
    return data[0]

def delete_preoder():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute("DELETE FROM storage_pre_order WHERE count = ?", (0,))
        con.commit()

def add_info_yoomoney(client_id, token, number):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_payment_yoomoney SET (yoomoney_number, yoomoney_token, yoomoney_client_id)  = (?, ?, ? )", (number, token, client_id))
        con.commit()

def get_yoomoney():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT yoomoney_token, yoomoney_client_id, yoomoney_number FROM storage_payment_yoomoney").fetchone()
        return data

def get_check_yoomoney():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT way_form FROM storage_payment_yoomoney").fetchone()
        return data[0]

def get_check_payok():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT way_form FROM storage_payment_payok").fetchone()
        return data[0]


def add_info_payok(api_key, api_id, secret_key, shop_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_payment_payok SET (api_key, api_id, secret_key, shop_id)  = (?, ?, ?, ?)", (api_key, api_id, secret_key, shop_id))
        con.commit()

def get_data_payok():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT api_key, api_id, secret_key, shop_id FROM storage_payment_payok").fetchone()
        return data



def get_check_payok():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT way_form FROM storage_payment_payok").fetchone()
        return data[0]


def get_check_paymanual():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT way_form FROM storage_payment_paymanual").fetchone()
        return data[0]

def update_pay_form(result):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_payment_yoomoney SET way_form = ?", (result,))
        con.commit()

def update_pay_form_payok(result):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_payment_payok SET way_form = ?", (result,))
        con.commit()

def update_pay_form_paymanual(result):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute(f"UPDATE storage_payment_paymanual SET way_form = ?", (result,))
        con.commit()

def delete_promocode_finl(promocode):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.execute("DELETE FROM storage_promocode WHERE promocode = ?", (promocode,))


def get_url():
    with sqlite3.connect(PATH_DATABASE) as con:
        data = con.execute(f"SELECT misc_support FROM storage_settings").fetchone()
        return data[0]



