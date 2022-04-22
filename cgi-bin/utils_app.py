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


db_credentials = get_credentials("rokk_db")[0]
db = connect(host=db_credentials['host'],
             user=db_credentials['user'],
             password=db_credentials['password'],
             database=db_credentials['database'],
             )
CURSOR = db.cursor()


def get_dish_id(CURSOR):
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


def get_iiko_biz_nomenclature():
    """
    Получает список номенклатур из iiko_biz, преобразует в список "название: айди"
    :return: dict
    """
    result = {}
    credentials = get_credentials('iiko_biz')[0]
    params = {
        "access_token": get_new_token(),
        "organization": credentials["organizationID"]
    }
    url = f'{credentials["host"]}nomenclature/{params["organization"]}'
    response = requests.get(url, params=params)
    json_Data = response.text
    dict_Data = json.loads(json_Data)
    products = dict_Data["products"]
    upload_date = dict_Data["uploadDate"]
    for i in products:
        result.update({i["name"]: i["id"]})
    return result, upload_date


iiko_biz_nomenclature = get_iiko_biz_nomenclature()[0]
upload_date = get_iiko_biz_nomenclature()[1]
accodion_ids_counter = 1

if is_logged_check() == "False":
    print_template('https://rokkwork.space/templates/unlogged_header.html')
    print_template('https://rokkwork.space/templates/unlogged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')
else:
    print_template('https://rokkwork.space/templates/logged_header.html')
    print('<script>document.title = "iiko utils App";</script>')

    # Printing main container:: Start #
    print('<div class="container">')

    print(
        '<p class="h3" style="margin-top: 1rem;">Перелік основних <small class="text-muted font-monospace">id</small></p>')

    print('<div class="accordion" id="accordionExample">')  # Открываем аккордеон
    print(f"""
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading{accodion_ids_counter}">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{accodion_ids_counter}" aria-expanded="false" aria-controls="collapse{accodion_ids_counter}">
                    Завантажені в iiko Biz.&nbsp;&nbsp;<span class="badge bg-secondary">Завантажено: {upload_date}</span>
                  </button>
                </h2>
            <div id="collapse{accodion_ids_counter}" class="accordion-collapse collapse" aria-labelledby="heading{accodion_ids_counter}" data-bs-parent="#accordionExample">
                <div class="accordion-body">
                    <table class="table table-striped">
                      <thead>
                        <tr>
                          <th scope="col">Назва</th>
                          <th scope="col"><code>id</code></th>
                        </tr>
                      </thead>
                        <tbody>
                    """)
    for i in iiko_biz_nomenclature:
        print(f'''
                <tr>
                  <td>{i}</td>
                  <td><code>{iiko_biz_nomenclature[i]}</code></td>
                </tr>
                ''')
    print("""       
                        <tbody>
                    </table>
                </div>
              </div>
            </div>
    """)
    accodion_ids_counter += 1
    print('</div>')  # закрываем аккордеон
    # Prnting main container::Ends #
    print('</div>')
    print_template('https://rokkwork.space/templates/footer.html')