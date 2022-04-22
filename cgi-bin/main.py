#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
import os
import cgi
from mysql.connector import connect, Error
import json
import time
import requests
import json
import sys
import codecs
import cgitb

cgitb.enable()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def is_logged_check():
    try:
        is_logged = os.environ['HTTP_COOKIE'].split("=")[1]
    except Exception:
        is_logged = "False"
    return is_logged



def print_template(url):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }
    html = requests.get(url, headers=headers)
    html.encoding = "utf-8"
    print(html.text)


def get_credentials():
    url = f'https://rokkwork.space/cgi-bin/credentials.json'
    headers = {'Accept': 'application/json', 'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    credentials = json.loads(response.text)
    return credentials


form = cgi.FieldStorage()
login = form.getfirst("login")
allowed_users = get_credentials()['users'][0]["tools_users"]


if login == "logout":
    print("Set-Cookie:is_logged = False;")
    print("Content-Type: text/html; charset=utf-8\n\n")
    print_template('https://rokkwork.space/templates/unlogged_header.html')
    print_template('https://rokkwork.space/templates/unlogged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')
elif login in allowed_users or os.environ['HTTP_COOKIE'].split("=")[1] == "True":
    print("Set-Cookie:is_logged = True;")
    print("Content-Type: text/html; charset=utf-8\n\n")
    print_template('https://rokkwork.space/templates/logged_header.html')
    print('<script>document.title = "Головна";</script>')
    print_template('https://rokkwork.space/templates/logged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')
else:
    print("Set-Cookie:is_logged = False;")
    print("Content-Type: text/html; charset=utf-8\n\n")
    print_template('https://rokkwork.space/templates/unlogged_header.html')
    print_template('https://rokkwork.space/templates/unlogged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')






