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


def get_coordinates(period_start, period_end):
    result = []
    CURSOR.execute(f"""
    SELECT latitude, longitude, created
    FROM heatmap
    WHERE created between '{period_start}' and '{period_end}';
    """)
    collected = CURSOR.fetchall()
    for i in collected:
        result.append([i[0], i[1]])
    return result


if is_logged_check() == "False":
    print_template('https://rokkwork.space/templates/unlogged_header.html')
    print_template('https://rokkwork.space/templates/unlogged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')
else:
    print_template('https://rokkwork.space/templates/logged_header.html')
    print('<script>document.title = "Heatmap App";</script>')
    print(f'''
    <h2 class="pb-2 border-bottom" style="padding-left: 3rem;">Теплова карта</h2>
    <form class="pure-form pure-form-stacked" action="/cgi-bin/heat_map.py" method="post">
    <div class="container">
      <div class="row">
        <div class="col-md-auto">
          <label for="start">Початок періоду:</label>
          <input type="date" id="start" name="start" class="form-control" />
        </div>
        <div class="col-md-auto">
          <label for="end">Кінець періоду:</label>
          <input type="date" id="end" name="end" class="form-control" />
        </div>
        <div class="col-md-auto" style="margin-top: auto;">
          <button type="submit" class="btn btn-primary">Створити</button>
        </div>
      </div>
    </div>
    </form>
    ''')
    print_template('https://rokkwork.space/templates/map.html')

    date_from = strftime("%Y-%m-%d")
    date_to = strftime("%Y-%m-%d")

    form = cgi.FieldStorage()

    start = form.getfirst("start", 0)
    end = form.getfirst("end", 0)

    if start != 0 and end != 0:
        start_day = start[8:10]
        start_month = start[5:7]
        start_year = start[0:4]
        end_day = end[8:10]
        end_month = end[5:7]
        end_year = end[0:4]
        date_from = f"{start_year}-{start_month}-{start_day}"
        date_to = f"{end_year}-{end_month}-{end_day}"
    else:
        date_from = strftime("%Y-%m-%d")
        date_to = strftime("%Y-%m-%d")

    for i in get_coordinates(date_from, date_to):
        a = f"L.marker({i},"
        b = '{icon: blueIcon}).addTo(mymap)'
        print(a + b)

    print('</script>')
    print('</div>')
    print_template('https://rokkwork.space/templates/footer.html')