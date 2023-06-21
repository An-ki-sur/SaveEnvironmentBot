import os
import ydb
import json
import binascii
import telebot
import requests
from telebot import types
from telebot.types import InputMediaPhoto
from geopy.geocoders import Nominatim

geolocator = Nominatim(timeout=10, user_agent = "myGeolocator")
driver = ydb.Driver(database='/ru-central1/b1gu0fk83o7tkm6us2l3/etnbifd536hjt2dsdvdg', endpoint ='grpcs://ydb.serverless.yandexcloud.net:2135', credentials=ydb.iam.MetadataUrlCredentials())

driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)
bot = telebot.TeleBot("5318941676:AAE65AOZ11ylYJJmajr1PoJ2yM41xMpTVLo", parse_mode=None)
id = ''
cat = ''
barcode = ''
loc = []
catsss = ["Все типы ♻", "Бумага📄", "Стекло🍾", "Пластик🫙", "Металл🎸", "Одежда👕", "Иное🏁", "Опасные отходы☠", "Батарейки🔋", "Лампочки💡", "Бытовая техника🔌", "ТетраПак🧃",
"Крышечки🔴", "Шины🛞"]

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn00 = types.KeyboardButton("🗺️Отправить геолокацию🗺️", request_location=True)
btn0 = types.KeyboardButton("Все типы ♻")
btn1 = types.KeyboardButton("Бумага📄")
btn2 = types.KeyboardButton("Стекло🍾")
btn3 = types.KeyboardButton("Пластик🫙")
btn4 = types.KeyboardButton("Металл🎸")
btn5 = types.KeyboardButton("Одежда👕")
btn6 = types.KeyboardButton("Иное🏁")
btn7 = types.KeyboardButton("Опасные отходы☠")
btn8 = types.KeyboardButton("Батарейки🔋")
btn9 = types.KeyboardButton("Лампочки💡")
btn10 = types.KeyboardButton("Бытовая техника🔌")
btn11 = types.KeyboardButton("ТетраПак🧃")
btn12 = types.KeyboardButton("Крышечки🔴")
btn13 = types.KeyboardButton("Шины🛞")
btn14 = types.KeyboardButton('Узнать куда выбросить❓️')
btn15 = types.KeyboardButton("Как отправить геолокацию боту?🆘")
btn16 = types.KeyboardButton("Увидеть свою статистику📈")
btn17 = types.KeyboardButton("Избранное💖")
btn19 = types.KeyboardButton("⬇Свернуть меню⬇")
btn20 = types.KeyboardButton("♻Экологический факт♻")
btn21 = types.KeyboardButton("Изменить имя для комментариев👤")
btn18 = types.KeyboardButton("Поддержать разработчиков🙌")
btn22 = types.KeyboardButton("Какой мусор можно сортировать?💌")
btn23 = types.KeyboardButton("Зачем нужно сортировать отходы?🚮")
markup.add(btn00)
markup.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13)
markup.add(btn20)
markup.add(btn14, btn21)
markup.add(btn16, btn17)
markup.add(btn15)
markup.add(btn23)
markup.add(btn18)

def get_nickname(session, id):
    nick = session.transaction().execute(
        f'''SELECT nickname FROM stats_pols
        WHERE TGid = "{id}"''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows[0]['nickname'].decode("utf-8")
    return nick




def add_like(session, data):
    currlike = session.transaction().execute(
        f'''SELECT liked_rec FROM stats_pols
        WHERE TGid = "{data[1]}"''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows[0]['liked_rec'].decode("utf-8")

    session.transaction().execute(
            f'''
            UPDATE stats_pols
            SET liked_rec = "{currlike + '-' + '+'.join([data[2], data[3]])}"
            WHERE TGid = "{data[1]}";
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    session.transaction().execute(
            f'''
            UPDATE all_recs
            SET times_like = times_like + 1
            WHERE lat = {data[2]} and lon = {data[3]};
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    bot.send_message(data[1], f"Вы добавили пункт сортировки в избранное")



def delete_like(session, data):
    currlike = session.transaction().execute(
        f'''SELECT liked_rec FROM stats_pols
        WHERE TGid = "{data[1]}"''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows[0]['liked_rec'].decode("utf-8")
    currlike = currlike.split('-')
    for i in currlike:
        if data[2] in i.split('+') and data[3] in i.split('+'):
            currlike.remove(i)
            break
    currlike = '-'.join(currlike)
    
    session.transaction().execute(
            f'''
            UPDATE stats_pols
            SET liked_rec = "{currlike}"
            WHERE TGid = "{data[1]}";
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    bot.send_message(data[1], f"Вы удалили пункт сортировки из избранного❌")
    

def send_liked(session):
    global id
    liked = session.transaction().execute(
        f'''
        SELECT liked_rec FROM stats_pols
        WHERE TGid = "{id}";
        ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['liked_rec']
    f = []

    for i in liked.decode('utf-8').split('-'):
        if i != '':
            f.append(session.transaction().execute(
                f'''
                SELECT * from all_recs WHERE 
                lat = {i.split('+')[0]} and lon = {i.split('+')[1]}''',
                commit_tx=True,
                settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0])

    if len(f) != 0:
        bot.send_message(id, f"Начинаю отправлять вам ваши любимые пункты💛")
    for i in f:
        tipe = []
        for j in i['cats'].split('='):
            if j != '':
                tipe.append(catsss[int(j)])
        locate = f"{i['lat']};{i['lon']}"
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button = types.InlineKeyboardButton(text="Удалить из избранного🗑️", callback_data=f"delete;{id};{locate}")
        callback_button1 = types.InlineKeyboardButton(text="Оставить комментарий✍🏻", callback_data=f"comment1;{id};{locate}")
        callback_button2 = types.InlineKeyboardButton(text="Посмотреть комментарии📋", callback_data=f"comment2;{id};{locate}")
        keyboard.add(callback_button, callback_button1, callback_button2)


        bot.send_message(id, f'''Название пункта приема: {binascii.unhexlify(i['name']).decode()}
Тип пункта сбора: *{', '.join(sorted(tipe))}*''', parse_mode='Markdown')
        bot.send_location(id, *tuple((float(i['lat']), float(i['lon']))), reply_markup=keyboard)
    if len(f) != 0:
        bot.send_message(id, f"Это все ваши избранные пункты сортировки мусора.💖")
    else:
        bot.send_message(id, f'К сожалению, вы ещё не добавляли пункты сортировки в избранное. Для этого необходимо нажать "Добавить в избранное" под найденным пунктом.💖')
        

def get_cat(session):
    global id, cat
    cat = session.transaction().execute(
        f'''SELECT cat FROM cats
        WHERE TGid = "{id}";''',
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows[0]['cat'].decode("utf-8")

def add_stat(session, id, result):
    global cat
    session.transaction().execute(
        f'''UPDATE stats_pols
        SET list_of_types = "{catsss[int(cat)]}", times_get = times_get + 1
        WHERE TGid = "{id}";''',
        commit_tx=True,
    )
    session.transaction().execute(
        f'''UPDATE all_recs
        SET times_find = times_find + 1
        WHERE id = {result[0]['id']} or id = {result[1]['id']} or id = {result[2]['id']};''',
        commit_tx=True,
    )


def change_curr_pos(session, newPos):
    global id, cat
    session.transaction().execute(
        f'''UPDATE cats
        SET pos = "{newPos}"
        WHERE TGid = "{id}";''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )

def execute_query(session):
    global id, cat
    session.transaction().execute(
    f'''
    UPDATE cats
    SET cat = "{cat}"
    WHERE TGid = "{id}";''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )



def change_bar(session):
    global id, cat, barcode
    a = session.transaction().execute(
        f'''SELECT cat FROM tovars
        WHERE bar = "{barcode}";''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows
    if a:
        bot.send_message(id, f"Это нужно выкинуть в {catsss[int(a[0]['cat'])]} \nМожете пользоваться ботом в стандартном режиме ")
        session.transaction().execute(
                f'''
                UPDATE cats
                SET pos = "0"
                WHERE TGid = "{id}";
            ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{id}")
        keyboard.add(callback_button)
        bot.send_message(id, f"К сожалению, мы не знаем, что это за товар. Просим нам помочь. Выберете из списка тип мусора для {barcode}", reply_markup=keyboard)
        

        session.transaction().execute(
        f'''
        UPDATE cats
        SET currBar = "{barcode}"
        WHERE TGid = "{id}"
    ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )
        session.transaction().execute(
        f'''
        UPDATE cats
        SET pos = "2"
        WHERE TGid = "{id}";
    ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )


    
def send_stats(session):
    f = session.transaction().execute(
        f'''SELECT times_get, times_sort, list_of_types FROM stats_pols
        WHERE TGid = "{id}";''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]
    a = f['list_of_types']
    bot.send_message(id, f"""Всего запросов: {f['times_get']}
Из них вы отсортировали отходы {f['times_sort']}
Последний тип: {a.decode('utf-8')}""")

    

def get_pos(session):
    return session.transaction().execute(
        f'''SELECT pos FROM cats
        WHERE TGid = "{id}";''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['pos'].decode("utf-8")


def new_pols(session):
    global id, cat
    
    # Create the transaction and execute query.
    f = list(map(lambda x: x['TGid'].decode("utf-8"), session.transaction().execute(
        'SELECT TGid FROM cats;',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows))


    if str(id) not in f:
        maxId = session.transaction().execute(
        'SELECT max(id) FROM cats;',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows[0]['column0']
        session.transaction().execute(
        f'''
        INSERT INTO cats(id, TGid, cat, currBar, pos) VALUES({maxId + 1},"{id}","{0}", "0", "0");''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
      )




    f = list(map(lambda x: x['TGid'].decode("utf-8"), session.transaction().execute(
        'SELECT TGid FROM stats_pols;',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows))


    if str(id) not in f:
        maxId = session.transaction().execute(
        'SELECT max(id) FROM stats_pols;',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows[0]['column0']
        session.transaction().execute(
        f'''
        INSERT INTO stats_pols(id, TGid, liked_rec, list_of_rec, list_of_types, times_get, times_sort, nickname) VALUES({maxId + 1},"{id}","", "", "0", 1, 0, "-");''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
      )




def newcat(session):
    maxId = int(max(session.transaction().execute(
        'SELECT id FROM tovars;',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )[0].rows, key=lambda x: int(x['id']))['id'])



    barcode = session.transaction().execute(
        f'''SELECT currBar FROM cats
        WHERE TGid = "{id}";''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['currBar'].decode("utf-8")
    if cat in catsss:

        session.transaction().execute(
            f'''
            INSERT INTO tovars(id, TGid, bar, cat) VALUES("{maxId + 1}","{id}","{barcode}", "{catsss.index(cat)}");''',
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )


    session.transaction().execute(
                f'''
                UPDATE cats
                SET pos = "0"
                WHERE TGid = "{id}";
            ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    bot.send_message(id, "Спасибо за обратную связь!\nЧтобы продолжить пользоваться ботом выберете один из пунктов меню")


def add_sorted(session, data):
    session.transaction().execute(
            f'''
            UPDATE stats_pols
            SET times_sort = times_sort + 1
            WHERE TGid = "{data[1]}";
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))

    session.transaction().execute(
            f'''
            UPDATE all_recs
            SET times_sort = times_sort + 1
            WHERE lat = {data[2]} and lon = {data[3]};
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    bot.send_message(data[1], f"♻️❤️Круто, что вы правильно сортируете отходы)❤️♻️")

def add_comment(session, text):
    global id
    data = session.transaction().execute(
    f'''SELECT currBar FROM cats
    WHERE TGid = "{id}";''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['currBar'].decode("utf-8").split(';')

    curr_com = session.transaction().execute(
    f'''SELECT comments FROM all_recs
    WHERE lat = {data[2]} and lon = {data[3]};''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['comments']
    if str(id) in curr_com:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button = types.InlineKeyboardButton(text="Посмотреть комментарии📑", callback_data=f"comment2;{data[1]};{data[2]};{data[3]}")
        callback_button1 = types.InlineKeyboardButton(text="Изменить свой🖍️", callback_data=f"edit;{data[1]};{data[2]};{data[3]}")
        callback_button2 = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{data[1]}")

        keyboard.add(callback_button, callback_button1, callback_button2)
        bot.send_message(data[1], f"Вы уже оставляли комментарий. Удалите или измените предыдущий", reply_markup=keyboard)
        return
    
    curr_com = curr_com + '||' + text + '___' + f"{data[1]}"

    session.transaction().execute(
            f'''
            UPDATE all_recs
            SET comments = "{curr_com}"
            WHERE lat = {data[2]} and lon = {data[3]};;
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))
    pool.retry_operation_sync(lambda x: change_curr_pos(x, 0))
    bot.send_message(id, "Теперь ваш отзыв могут увидеть другие пользователи🗯️")
    

def save_data(session, data):
    session.transaction().execute(
        f'''
        UPDATE cats
        SET currBar = "{data}"
        WHERE TGid = "{data.split(';')[1]}"
    ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )

def read_comments(session, data):

    bot.send_message(data[1], f"""Начинаю отправлять вам комментарии📨""")

    curr_com = session.transaction().execute(
    f'''SELECT comments FROM all_recs
    WHERE lat = {data[2]} and  lon = {data[3]};''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['comments'].split('||')

    

    for i in curr_com:
        if i != '' and i != '-':

            keyboard = types.InlineKeyboardMarkup(row_width=2)
            if i.split('___')[1] == data[1]:
                callback_button = types.InlineKeyboardButton(text="🖍️Изменить🖍️", callback_data=f"edit;{';'.join(data[1:])}")
                callback_button1 = types.InlineKeyboardButton(text="🗑️Удалить🗑️", callback_data=f"delete_com;{';'.join(data[1:])}")
                keyboard.add(callback_button, callback_button1)
                nick = session.transaction().execute(
                f'''SELECT nickname FROM stats_pols
                WHERE TGid = "{i.split('___')[1]}"''',
                commit_tx=True,
                settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['nickname'].decode('utf-8')
                bot.send_message(data[1], f"""🗣️*{binascii.unhexlify(nick).decode()}(Вы)*:
{i.split('___')[0]}""", parse_mode='Markdown', reply_markup=keyboard)

            else:
                

                nick = session.transaction().execute(
                    f'''SELECT nickname FROM stats_pols
                    WHERE TGid = "{i.split('___')[1]}"''',
                    commit_tx=True,
                    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['nickname'].decode('utf-8')


                bot.send_message(data[1], f"""🗣️*{binascii.unhexlify(nick).decode()}*:
{i.split('___')[0]}""", parse_mode='Markdown')


    keyboard = types.InlineKeyboardMarkup(row_width=2)
    callback_button2 = types.InlineKeyboardButton(text="Оставить комментарий✍🏻", callback_data=f"comment1;{';'.join(data[1:])}")
    keyboard.add(callback_button2)
    bot.send_message(data[1], f"Это все комментарии. Вы можете остаить свой!", reply_markup=keyboard)
    pool.retry_operation_sync(lambda x: change_curr_pos(x, 0))

def delete_comm(session, data):
    curr_com = session.transaction().execute(
    f'''SELECT comments FROM all_recs
    WHERE lat = {data[2]} and  lon = {data[3]};''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['comments'].split('||')
    for i in curr_com:
        if data[1] in i:
            curr_com.remove(i)
            break
    
    curr_com = '||'.join(curr_com)
    session.transaction().execute(
            f'''
            UPDATE all_recs
            SET comments = "{curr_com}"
            WHERE lat = {data[2]} and lon = {data[3]};;
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))

def send_fact(session, id):
    fact = session.transaction().execute(
    f'''SELECT fact, RandomNumber(fact) as r FROM facts
order by r
limit 1''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['fact']
    bot.send_message(id, fact + "♻️")

def edit_comm(session, id, text):
    data = session.transaction().execute(
    f'''SELECT currBar FROM cats
    WHERE TGid = "{id}"''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['currBar'].decode('utf-8').split(';')

    curr_com = session.transaction().execute(
    f'''SELECT comments FROM all_recs
    WHERE lat = {data[2]} and  lon = {data[3]};''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))[0].rows[0]['comments'].split('||')

    for i in range(len(curr_com)):
        if str(id) in curr_com[i]:
            curr_com[i] = text + '___' + str(id)
    
    curr_com = '||'.join(curr_com)

    session.transaction().execute(
            f'''
            UPDATE all_recs
            SET comments = "{curr_com}"
            WHERE lat = {data[2]} and lon = {data[3]};;
        ''',
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))

    bot.send_message(data[1], f"Ваш комментарий изменён📚")



def handler(event, context):
    global id, cat, barcode, markup
    
    if 'callback_query' in json.loads(event['body']):
        body = json.loads(event['body'])
        data = body['callback_query']['data'].split(';')
        if data[0] == 'back':
            pool.retry_operation_sync(lambda x: change_curr_pos(x, 0))
            bot.send_message(data[1], f"Вы можете продолжать пользоваться ботом в стандартном режиме.✅")
        if data[0] == 'location':
            ins1 = requests.get('https://storage.yandexcloud.net/env-backet/Bot1.jpg').content
            ins2 = requests.get('https://storage.yandexcloud.net/env-backet/bot2.jpg').content
            ins3 = requests.get('https://storage.yandexcloud.net/env-backet/bot3.jpg').content

            media_group = []
            a = "🌎Для отправки геолокации необходимо нажать кнопку в меню.\n\nЛибо нажать скрепку, после чего выбрать *Location* и нажать *Send My Current Location*🌎"
            media_group.append(InputMediaPhoto(ins1, caption = a, parse_mode='Markdown'))
            media_group.append(InputMediaPhoto(ins2, caption = ''))
            media_group.append(InputMediaPhoto(ins3, caption = ''))
            bot.send_media_group(data[1], media_group)

        if data[0] == 'like':
            pool.retry_operation_sync(lambda x: add_like(x, data))
            
        if data[0] == 'edit':
            pool.retry_operation_sync(lambda x: change_curr_pos(x, 9))
            bot.send_message(data[1], f"Напишите изменённый комментарий.✍️")
            pool.retry_operation_sync(lambda x: save_data(x, body['callback_query']['data']))
        if data[0] == 'delete_com':
            pool.retry_operation_sync(lambda x: delete_comm(x, data))
            bot.send_message(data[1], "💥Вы удалили комментарий!💥")


        if data[0] == 'delete':
            pool.retry_operation_sync(lambda x: delete_like(x, data))
        if data[0] == 'sort':
            pool.retry_operation_sync(lambda x: add_sorted(x, data))
        if data[0] == 'comment1':
            nick = pool.retry_operation_sync(lambda x: get_nickname(x, data[1]))
            if  nick != '-':
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{data[1]}")
                keyboard.add(callback_button)

                pool.retry_operation_sync(lambda x: change_curr_pos(x, 5))
                pool.retry_operation_sync(lambda x: save_data(x, body['callback_query']['data']))
                bot.send_message(data[1], f"Напишите ваш комментарий или отзыв про пункт сортировки.🗣️", reply_markup=keyboard)
            else:
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{id}")
                keyboard.add(callback_button)
                bot.send_message(data[1], f"Пожалйста, напишите ваше имя", reply_markup=keyboard)
                pool.retry_operation_sync(lambda x: change_curr_pos(x, 8))
                pool.retry_operation_sync(lambda x: save_data(x, body['callback_query']['data']))
        if data[0] == 'comment2':
            pool.retry_operation_sync(lambda x: read_comments(x, data))
        if data[0] == 'text_loc':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{data[1]}")
            keyboard.add(callback_button)
            pool.retry_operation_sync(lambda x: change_curr_pos(x, 6))
            bot.send_message(data[1], f"Напишите адрес текстом.🗒️\nБез сокращений и знаков препинания. Пример: Москва Малая Семёновская 15", reply_markup=keyboard)

        
    elif 'message' in  json.loads(event['body']):
        body = json.loads(event['body'])
        id = body['message']['chat']['id']
        pool.retry_operation_sync(new_pols)
        if pool.retry_operation_sync(get_pos) == '0':
            if 'location' in body['message'].keys():
                finder(body)
            
            elif 'text' in body['message'].keys():
                id = str(body['message']['chat']['id'])
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                callback_button = types.InlineKeyboardButton(text="🆘Узнать, как отправить геолокацию🆘", callback_data=f"location;{body['message']['chat']['id']}")
                callback_button1 = types.InlineKeyboardButton(text="🪶Ввести адрес текстом🪶", callback_data=f"text_loc;{body['message']['chat']['id']}")
                keyboard.add(callback_button, callback_button1)
                if body['message']['text'] == '/start':
                    pool.retry_operation_sync(new_pols)

                    bot.send_message(body['message']['chat']['id'], '''Здравствуйте! 

Я бот, который поможет вам сохранить Землю в чистоте. 🌱♻️

Я подскажу вам, где находится ближайший пункт по сортировке отходов. Отправьте мне вашу геолокацию для поиска ближайших сортировок мусора. 

А так же заходите на наш сайт: https://env-site.website.yandexcloud.net

Если в работе бота вы обнаружили какие либо ошибки, то напишите @AntonIvanov1111 для решения проблемы.''',
                                    reply_markup=markup)
                elif 'Все типы' in body['message']['text']:
                    cat = '0'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для всех типов♻", reply_markup=keyboard)
                elif 'Бумага' in body['message']['text']:
                    cat = '1'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для бумаги📄", reply_markup=keyboard)
                elif 'Стекло' in body['message']['text']:
                    cat = '2'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для стекла🍾", reply_markup=keyboard)
                elif 'Пластик' in body['message']['text']:
                    cat = '3'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для пластика🫙", reply_markup=keyboard)
                elif 'Металл' in body['message']['text']:
                    cat = '4'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для металла🎸", reply_markup=keyboard)
                elif 'Одежда' in body['message']['text']:
                    cat = '5'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для одежды👕", reply_markup=keyboard)
                elif 'Иное' in body['message']['text']:
                    cat = '6'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для иного🏁", reply_markup=keyboard)
                elif 'Опасные отходы' in body['message']['text']:
                    cat = '7'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для опасных отходов☠", reply_markup=keyboard)
                elif 'Батарейки' in body['message']['text']:
                    cat = '8'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для батареек🔋", reply_markup=keyboard)
                elif 'Лампочки' in body['message']['text']:
                    cat = '9'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для лампочек💡", reply_markup=keyboard)
                elif 'Бытовая техника' in body['message']['text']:
                    cat = '10'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для бытовой техники🔌", reply_markup=keyboard)
                elif 'ТетраПак' in body['message']['text']:
                    cat = '11'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для тетра пака🧃", reply_markup=keyboard)
                elif 'Крышечки' in body['message']['text']:
                    cat = '12'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для крышечек🔴", reply_markup=keyboard)
                elif 'Шины' in body['message']['text']:
                    cat = '13'
                    pool.retry_operation_sync(execute_query)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте геолокацию для поиска ближайших пунктов сортировки для шин🛞", reply_markup=keyboard)
                elif 'Узнать куда выбросить' in body['message']['text']:
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{body['message']['chat']['id']}")
                    keyboard.add(callback_button)
                    bot.send_message(body['message']['chat']['id'],
                                    "Отправьте, пожалуйста номер с ▌│█║▌║▌║ штрих-кода ▌│█║▌║▌║ товара (для сканирования можете использовать следующего бота: @QRVisorBot)", reply_markup=keyboard)
                    
                    pool.retry_operation_sync(lambda x: change_curr_pos(x, 1))

                elif 'Увидеть свою статистику' in body['message']['text']:
                    pool.retry_operation_sync(send_stats)
                elif 'Свернуть меню' in body['message']['text']:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn0 = types.KeyboardButton("♻️Открыть меню♻️")
                    markup.add(btn0)
                    bot.send_message(body['message']['chat']['id'],
                                        '''Меню убрано💫''',  reply_markup=markup) 

                elif 'Как отправить геолокацию боту?' in body['message']['text']:
                    ins1 = requests.get('https://storage.yandexcloud.net/env-backet/instructon-1.jpeg').content
                    ins2 = requests.get('https://storage.yandexcloud.net/env-backet/instruction-2.jpeg').content

                    media_group = []
                    a = "🌎Для отправки геолокации необходимо нажать скрепку, там выбрать *Location* и нажать *Send My Current Location*🌎"
                    media_group.append(InputMediaPhoto(ins1, caption = a, parse_mode='Markdown'))
                    media_group.append(InputMediaPhoto(ins2, caption = ''))
                    bot.send_media_group(body['message']['chat']['id'], media_group)
                
                elif 'Избранное' in body['message']['text']:
                    pool.retry_operation_sync(send_liked)
                elif 'Экологический факт' in body['message']['text']:
                    bot.send_message(body['message']['chat']['id'], f"Сейчас поищу интересный факт в своей копилке🌎")
                    pool.retry_operation_sync(lambda x: send_fact(x, body['message']['chat']['id']))
                elif 'Изменить имя' in body['message']['text']:
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{body['message']['chat']['id']}")
                    keyboard.add(callback_button)
                    bot.send_message(body['message']['chat']['id'], f"Пожалйста, напишите ваше имя", reply_markup=keyboard)
                    pool.retry_operation_sync(lambda x: change_curr_pos(x, 10))
                elif 'Поддержать разработчиков' in body['message']['text']:
                    bot.send_message(body['message']['chat']['id'],
                                    "Данный проект создан энтузиастами и не имеет абсолютно никакого финансирования. Но содержание серверов и баз данных требует вложений. Мы будем очень благодарны каждому, кто поддержит нас материально.\n Пожертвование можно внести по ссылке: https://www.donationalerts.com/r/mof1us. Каждый донат положительно скажется на работоспособности бота.😊")
                elif 'Зачем нужно сортировать отходы?' in body['message']['text']:
                    ins1 = requests.get('https://storage.yandexcloud.net/env-backet/1.png').content
                    ins2 = requests.get('https://storage.yandexcloud.net/env-backet/2.png').content
                    ins3 = requests.get('https://storage.yandexcloud.net/env-backet/3.png').content

                    media_group = []
                    media_group.append(InputMediaPhoto(ins1, caption = '''Раздельный сбор отходов необходим для того, чтобы из ТБО (Твердые Бытовые Отходы) выделять полезные материалы, годные для переработки и повторного использования.

Сортировка отходов на раннем этапе – до того, как они отправятся на помойку – решает несколько задач:

♻️ сокращает общее количество отходов на планете
♻️ снижает количество потребляемых природных ресурсов за счет повторного применения сырья
♻️ способствует улучшению экологической ситуации в мире
♻️ уменьшает затраты на вторичную переработку''', parse_mode='Markdown'))
                    media_group.append(InputMediaPhoto(ins2, caption = ''))
                    media_group.append(InputMediaPhoto(ins3, caption = ''))
                    bot.send_media_group(body['message']['chat']['id'], media_group)
                elif 'Открыть меню' in body['message']['text']:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn00 = types.KeyboardButton("🗺️Отправить геолокацию🗺️", request_location=True)
                    btn0 = types.KeyboardButton("Все типы ♻")
                    btn1 = types.KeyboardButton("Бумага📄")
                    btn2 = types.KeyboardButton("Стекло🍾")
                    btn3 = types.KeyboardButton("Пластик🫙")
                    btn4 = types.KeyboardButton("Металл🎸")
                    btn5 = types.KeyboardButton("Одежда👕")
                    btn6 = types.KeyboardButton("Иное🏁")
                    btn7 = types.KeyboardButton("Опасные отходы☠")
                    btn8 = types.KeyboardButton("Батарейки🔋")
                    btn9 = types.KeyboardButton("Лампочки💡")
                    btn10 = types.KeyboardButton("Бытовая техника🔌")
                    btn11 = types.KeyboardButton("ТетраПак🧃")
                    btn12 = types.KeyboardButton("Крышечки🔴")
                    btn13 = types.KeyboardButton("Шины🛞")
                    btn14 = types.KeyboardButton('❓️Узнать куда выбросить❓️')
                    btn15 = types.KeyboardButton("Как отправить геолокацию боту?🆘")
                    btn16 = types.KeyboardButton("Увидеть свою статистику📈")
                    btn17 = types.KeyboardButton("Избранное💖")
                    btn19 = types.KeyboardButton("⬇Свернуть меню⬇")
                    btn20 = types.KeyboardButton("♻Экологический факт♻")
                    btn21 = types.KeyboardButton("Изменить имя для комментариев👤")
                    btn18 = types.KeyboardButton("Поддержать разработчиков🙌")
                    btn22 = types.KeyboardButton("Какой мусор можно сортировать?💌")
                    markup.add(btn00)
                    markup.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13)
                    markup.add(btn20)
                    markup.add(btn14, btn21)
                    markup.add(btn16, btn17)
                    markup.add(btn15)
                    markup.add(btn18)
                    bot.send_message(body['message']['chat']['id'], "Меню открыто. Спасибо, что сохраняете нашу планету в чистоте💖",  reply_markup=markup)
                else:
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    callback_button = types.InlineKeyboardButton(text="🆘Узнать, как🆘", callback_data=f"location;{body['message']['chat']['id']}")
                    callback_button1 = types.InlineKeyboardButton(text="Отправить адрес текстом🪶", callback_data=f"text_loc;{body['message']['chat']['id']}")
                    keyboard.add(callback_button, callback_button1)
                    bot.send_message(body['message']['chat']['id'], "🌎Отправьте пожалуйста геолокацию🌎", reply_markup=keyboard)
        elif pool.retry_operation_sync(get_pos) == '1':
            if 'text' in body['message']:
                barcode = body['message']['text']
                pool.retry_operation_sync(change_bar)
        elif pool.retry_operation_sync(get_pos) == '2':
            if 'text' in body['message']:
                cat = body['message']['text']
                pool.retry_operation_sync(newcat)
        elif pool.retry_operation_sync(get_pos) == '5':
            if 'text' in body['message']:
                pool.retry_operation_sync(lambda x: add_comment(x, body['message']['text']))
                
        elif pool.retry_operation_sync(get_pos) == '6':
            if 'text' in body['message']:
                coords = geolocator.geocode(body['message']['text'])
                if coords:
                    coords = (coords.longitude, coords.latitude)
                    finder(body, is_text=True, coords=coords)
                    pool.retry_operation_sync(lambda x: change_curr_pos(x, 0))
                else:
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    callback_button = types.InlineKeyboardButton(text="Вернуться назад🔙", callback_data=f"back;{body['message']['chat']['id']}")
                    keyboard.add(callback_button)
                    bot.send_message(body['message']['chat']['id'], "❌К сожалению, не удалось распознать адрес. Попробуйте другой. Не забудьте указать город, по которому вы ищите.❌", reply_markup=keyboard)
        elif pool.retry_operation_sync(get_pos) == '8':
            if 'text' in body['message']:
                pool.retry_operation_sync(lambda x: add_nick(x, body['message']['chat']['id'], body['message']['text']))
                pool.retry_operation_sync(lambda x: change_curr_pos(x, 5))
                bot.send_message(body['message']['chat']['id'], "Теперь напишите ваш комментарий!✍️")
        elif pool.retry_operation_sync(get_pos) == '9':
            if 'text' in body['message']:
                pool.retry_operation_sync(lambda x: edit_comm(x, body['message']['chat']['id'], body['message']['text']))
                pool.retry_operation_sync(lambda x: change_curr_pos(x, 0))
        elif pool.retry_operation_sync(get_pos) == '10':
            if 'text' in body['message']:
                pool.retry_operation_sync(lambda x: add_nick(x, body['message']['chat']['id'], body['message']['text']))
                pool.retry_operation_sync(lambda x: change_curr_pos(x, 0))
                bot.send_message(body['message']['chat']['id'], "✅Ваше имя изменено✅")

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'method': 'sendMessage',
        }),
        'isBase64Encoded': False
    }



def add_nick(session, id, nick):
    session.transaction().execute(
        f'''
        UPDATE stats_pols SET nickname = "{nick.encode("utf-8").hex()}" WHERE TGid = "{id}"
        ''',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2))

def get_sorts(session, cat, lon, lat):
    if cat == '0':
        return session.transaction().execute(
        f'''
        SELECT * from all_recs ORDER BY (lon - {lon})  * (lon - {lon}) + (lat - {lat}) * (lat - {lat}) LIMIT 3
        ''')[0].rows
    else:
        return session.transaction().execute(
        f'''
        SELECT * from all_recs WHERE cats LIKE "%={cat}=%" ORDER BY (lon - {lon})  * (lon - {lon}) + (lat - {lat}) * (lat - {lat}) LIMIT 3
        ''')[0].rows

def finder(body, is_text = False, coords=None):
    global cat, loc
    pool.retry_operation_sync(get_cat)


    bot.send_message(body['message']['chat']['id'], f'''🔎Поиск начинается.🔍 
Выбраный тип отходов: {catsss[int(cat)]}''')
    if not is_text:
        lon, lat = body['message']['location']['longitude'], body['message']['location']['latitude']
    else:
        lon, lat = coords

    result = pool.retry_operation_sync(lambda x: get_sorts(x, cat, lon, lat))
    pool.retry_operation_sync(lambda x: add_stat(x, body['message']['chat']['id'], result))
    for i in result:
        tipe = []
        for j in i['cats'].split('='):
            if j != '':
                tipe.append(catsss[int(j)])

        bot.send_message(body['message']['chat']['id'], f'''Название пункта приема: {binascii.unhexlify(i['name']).decode()}

Тип пункта сбора: *{', '.join(sorted(tipe))}*
        ''', parse_mode='Markdown')
        locate = f"{i['lat']};{i['lon']}"
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button = types.InlineKeyboardButton(text="Добавить в избранное💖", callback_data=f"like;{body['message']['chat']['id']};{locate}")
        callback_button1 = types.InlineKeyboardButton(text="Я отсортировал здесь♻️", callback_data=f"sort;{body['message']['chat']['id']};{locate}")
        callback_button2 = types.InlineKeyboardButton(text="Оставить комментарий✍🏻", callback_data=f"comment1;{body['message']['chat']['id']};{locate}")
        callback_button3 = types.InlineKeyboardButton(text="Посмотреть комментарии📋", callback_data=f"comment2;{body['message']['chat']['id']};{locate}")
        keyboard.add(callback_button, callback_button1, callback_button2, callback_button3)

        bot.send_location(body['message']['chat']['id'], *tuple((float(i['lat']), float(i['lon']))), reply_markup=keyboard)

        loc.append(locate)

    bot.send_message(body['message']['chat']['id'],
                     '''✅Поиск окончен.✅ 
Если вы обнаружили ошибки в работе бота, то напишите разработчику в Telegram: @AntonIvanov1111''', reply_markup=markup) 
