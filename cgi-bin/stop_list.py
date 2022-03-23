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


def is_logged_check():
    try:
        is_logged = os.environ['HTTP_COOKIE'].split("=")[1]
    except Exception:
        is_logged = "False"
    return is_logged


print(is_logged_check())