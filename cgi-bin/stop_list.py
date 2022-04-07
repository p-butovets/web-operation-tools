#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
print("Content-Type: text/html; charset=utf-8\n\n")
from mysql.connector import connect, Error
import os
import sys
import codecs
import cgitb
import cgi
import json
import requests
from time import strftime

cgitb.enable()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def print_template(url):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }
    html = requests.get(url, headers=headers)
    html.encoding = "utf-8"
    print(html.text)


def is_logged_check():
    try:
        is_logged = os.environ['HTTP_COOKIE'].split("=")[1]
    except Exception:
        is_logged = "False"
    return is_logged


def get_credentials(project_name):
    url = f'https://rokkwork.space/cgi-bin/credentials.json'
    headers = {'Accept': 'application/json', 'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    credentials = json.loads(response.text)[project_name]
    return credentials


def get_new_token():
    credentials = get_credentials('iiko_biz')[0]
    url = f'{credentials["host"]}auth/access_token?user_id={credentials["user"]}&user_secret={credentials["password"]}'
    token = requests.get(url).text.replace('"', '')
    return token


def get_stop_list(CURSOR):
    credentials = get_credentials('iiko_biz')[0]
    params = {
        "access_token": get_new_token(),
        "organization": credentials["organizationID"]
    }
    url = f'{credentials["host"]}stopLists/getDeliveryStopList'
    response = requests.get(url, params=params)
    json_Data = response.text
    dict_Data = json.loads(json_Data)
    all_orders = dict_Data["stopList"]

    result = []
    for i in all_orders:
        terminal_id = i['deliveryTerminalId']
        CURSOR.execute(f'SELECT iiko_kitchen_name FROM kitchen_id WHERE iiko_terminal_id = "{terminal_id}"')
        kitchen_name = CURSOR.fetchone()[0]
        info_block = {
            'Кухня': kitchen_name,
            'Блюда на стопе': []
        }
        for dish in i['items']:
            dish_id = dish['productId']
            CURSOR.execute(f'SELECT iiko_dish_name FROM dish_id WHERE iiko_dish_id = "{dish_id}"')
            dish_name = CURSOR.fetchone()[0]
            dish_balance = dish["balance"]
            info_block['Блюда на стопе'].append({dish_name: dish_balance})
        result.append(info_block)
    return result


if is_logged_check() == "False":
    print_template('https://rokkwork.space/templates/unlogged_header.html')
    print_template('https://rokkwork.space/templates/unlogged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')
else:
    print_template('https://rokkwork.space/templates/logged_header.html')

    db_credentials = get_credentials("rokk_db")[0]
    db = connect(host=db_credentials['host'],
                 user=db_credentials['user'],
                 password=db_credentials['password'],
                 database=db_credentials['database'],
                 )
    CURSOR = db.cursor()

    print(f'''
        <h2 class="pb-2 border-bottom" style="padding-left: 3rem;">Актуальный стоп-лист</h2>
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4 py-5" style="padding-left: 3rem; padding-right: 3rem;">
        ''')
    for i in get_stop_list(CURSOR):
        print(f'''
            <div class="col d-flex align-items-start">
                <div>
                    <h4 class="fw-bold mb-0" style="
                                                    padding: 0.5rem 0.5rem 0.5rem 0.25rem;
                                                    background-color: #3D5A80;
                                                    color: white;
                                                    border-radius: 0.25rem;
                                                "><ion-icon name="home-outline"></ion-icon> {i['Кухня']}</h4>
        ''')
        for k in i['Блюда на стопе']:
            for j in k:
                print(f'<p style="margin-bottom: 0px;">{j}...{k[j]}</p>')
        print(f'''
            </div>
            </div>    
        ''')
    print("</div>")
    print_template('https://rokkwork.space/templates/footer.html')