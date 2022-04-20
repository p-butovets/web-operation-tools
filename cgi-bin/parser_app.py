#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
print("Content-Type: text/html; charset=utf-8\n\n")
import xml.etree.ElementTree as ET
import re
import os
import sys
import codecs
import cgitb
import cgi
import requests

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


if is_logged_check() == "False":
    print_template('https://rokkwork.space/templates/unlogged_header.html')
    print_template('https://rokkwork.space/templates/unlogged_main.html')
    print_template('https://rokkwork.space/templates/footer.html')
else:
    print_template('https://rokkwork.space/templates/logged_header.html')

    # Printing main container:: Start #

    print('<div class="container">')

    tree = ET.parse('maps/doc.kml')
    root = tree.getroot()
    namespace = re.match('\{(.*?)\}kml', root.tag).group(1)
    ns = {'def': namespace}
    coord_ex = '(-?\d+\.\d+),'
    heig_ex = '(\d+)'
    regex = coord_ex + coord_ex + heig_ex

    map_credits = """
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYnV0b3ZldHNwYXZlbCIsImEiOiJja3RtdXZqZ24wbXdvMnBvM3YwMXVmd2pqIn0.kszzbUxf3zKl7M359TnVIA', {
	maxZoom: 18,
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
		'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>' + ' | for <a href="https://bagatolososia.kiev.ua/">БагатоЛосося</a> ',
	id: 'mapbox/streets-v11',
	tileSize: 512,
	zoomOffset: -1
    })
    """

    print('''
    <p class="h3" style="margin-top: 1rem;">JavaScript переменные для вставки в <small class="text-muted font-monospace">templates/map.html</small></p>
    ''')
    print('''
    <div class="accordion" id="accordionExample">
    ''')

    accodion_ids_counter = 1

    # extract and transform coordinates from kml to var polygon
    for i in root.findall('.//def:Placemark', ns):
        heatmap = []
        name = i.find('def:name', ns).text
        coord = i.find('.//def:coordinates', ns)
        if not coord is None:
            coord = coord.text.strip()
            coord = re.findall(regex, coord)
            for (long, lat, heig) in coord:
                item = [lat, long]
                heatmap.append(item)
        heatmap_result = {
            'name': name,
            'html': f"var polygon = L.polygon({heatmap}).addTo(mymap).bindPopup('{name}');"
        }

        print(f"""
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading{accodion_ids_counter}">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{accodion_ids_counter}" aria-expanded="false" aria-controls="collapse{accodion_ids_counter}">
                <span class="badge bg-secondary">{heatmap_result['name']}</span>
              </button>
            </h2>
            <div id="collapse{accodion_ids_counter}" class="accordion-collapse collapse" aria-labelledby="heading{accodion_ids_counter}" data-bs-parent="#accordionExample">
              <div class="accordion-body">
                {heatmap_result['html']}
                <div id="mapid{accodion_ids_counter}" style="height: 200px; margin-top: 1rem;"></div>
                <script>
                var mymap{accodion_ids_counter} = L.map("mapid{accodion_ids_counter}").setView([50.45620065316121, 30.504618701624874], 10);
                {map_credits}.addTo(mymap{accodion_ids_counter});
                var polygon = L.polygon({heatmap}).addTo(mymap{accodion_ids_counter}).bindPopup('{name}');
                </script>
              </div>
            </div>
      </div>
        """)
        accodion_ids_counter += 1
    print('</div>')  # закрываем аккордеон

    print('''
    <p class="h3" style="margin-top: 1rem;">Поле <small class="text-muted font-monospace">'json'</small> в таблице <small class="text-muted font-monospace">oc_polygons</small></p>
    ''')
    print('''
    <div class="accordion" id="accordionExample">
    ''')

    accodion_ids_counter = 50

    # extract and transform coordinates from kml for site db
    for i in root.findall('.//def:Placemark', ns):
        site_coords = []
        name = i.find('def:name', ns).text
        coord = i.find('.//def:coordinates', ns)
        if not coord is None:
            coord = coord.text.strip()
            coord = re.findall(regex, coord)
            for (long, lat, heig) in coord:
                item = {'lng': long, 'lat': lat}
                site_coords.append(item)
        site_coords_result = {
            'name': name,
            'text': str(site_coords).replace("'", "")
        }
        print(f"""
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading{accodion_ids_counter}">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{accodion_ids_counter}" aria-expanded="false" aria-controls="collapse{accodion_ids_counter}">
                <span class="badge bg-secondary">{site_coords_result['name']}</span>
              </button>
            </h2>
            <div id="collapse{accodion_ids_counter}" class="accordion-collapse collapse" aria-labelledby="heading{accodion_ids_counter}" data-bs-parent="#accordionExample">
              <div class="accordion-body">
                {site_coords_result['text']}
              </div>
            </div>
      </div>
        """)
        accodion_ids_counter += 1
    print('</div>')  # закрываем аккордеон

    # Prnting main container::Ends #
    print('</div>')
    print_template('https://rokkwork.space/templates/footer.html')