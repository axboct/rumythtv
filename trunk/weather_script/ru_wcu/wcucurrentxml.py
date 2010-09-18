#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script is partially based on script dwua_xml.pl by Victor Bron 
import math
import string
import time
import datetime
import urllib2
import urllib
import os
import sys
import traceback
import codecs
from optparse import OptionParser
from lxml import etree

name = 'WCU-Current-XML';
version = 0.01;
author = 'Alex Vasilyev';
email = 'sandybigboy@gmail.com';

update_timeout = 120*60
retrieve_timeout = 30

data_fields = ('cclocation', 'station_id', 'copyright',
        'observation_time', 'weather', 'temp', 'relative_humidity',
        'wind_dir', 'pressure', 'visibility', 'weather_icon',
        'appt', 'wind_spdgst')

icons = {'_0_moon.gif' : 'sunny.png',  '_0_sun.gif' :  'sunny.png',  '_1_moon_cl.gif' :  'pcloudy.png', 
            '_1_sun_cl.gif' : 'pcloudy.png',  '_2_cloudy.gif' : 'mcloudy.png', '_3_pasmurno.gif' :  'cloudy.png', 
            '_4_short_rain.gif' : 'lshowers.png', '_5_rain.gif' : 'showers.png',  
            '_6_lightning.gif' : 'thunshowers.png', '_7_hail.gif' :  'fog.png', 
            'ico=~/^_8_rain_snow.gif' :  'rainsnow.png', 'ico=~ /_9_snow.gif' : 'snowshow.png',  '_10_heavy_snow.gif' :  'snowshow.png', 
            '_255_NA.gif' : 'unknown.png'
             }
    
#weather = {255 : "N/A", 10 : "Clear", 20 : "Cloudly", 30 : "Clear/Cloudly", 40 : "Pasmurno", 50 : "Short Rain", 
#                    60 : "Rain",  70 : "Hail", 80 : "Rain with snow",  90 : "Snow",  100 : "Heavy Snow"
#                    }
weather = {25 : "Н/Д", 0 : "Ясно", 1 : "С прояснениями", 2 : "Перем. облачность", 3 : "Пасмурно", 4 : "Небольшой дождь", 
                    5 : "Дождь",  6 : "Гроза",  7 : "Град", 8 : "Снег с дождем",  9 : "Снег",  10 : "Сильный снег"
                    }
#wind_dir = {255 : "N/A", 20 : "N", 35 : "NNE", 55 : "NE",  70 : "ENE", 110 : "E", 125 : "ESE", 145 : "SE", 160 : "SSE", 
                    #200 : "S", 215 : "SSW", 235 : "SW", 250 : "WSW", 290 : "W", 305 : "WNW",  325 : "NW", 340 : "NNW", 360 : "N"
                #}
wind_dir = {255 : "Н/Д", 20 : "С", 35 : "ССЗ", 55 : "СВ",  70 : "ВСВ", 110 : "В", 125 : "ВЮВ", 145 : "ЮВ", 160 : "ЮЮВ", 
                    200 : "Ю", 215 : "ЮЮЗ", 235 : "ЮЗ", 250 : "ЗЮЗ", 290 : "З", 305 : "ЗСЗ",  325 : "СЗ", 340 : "ССЗ", 360 : "С"
                }                

def comment_out(str):
	s = str
	try:
		s = unicode(str, "utf8")
	except:
		pass

	print("# %s" % (s,))

def print_exception(str):
	for line in str.splitlines():
		comment_out(line)

def get_page(address,  title=''):
    data={}
    req = urllib2.Request(address, data)
    response = urllib2.urlopen(req)
    if response.code == 200:
        pagedata = response.read()
        return pagedata
    else:
        return None
        raise Exception( "get_page() error: ",response.code)   

def get_timeouts():
    sys.stdout.write( u'%s, %s\n' % (update_timeout, retrieve_timeout))

def get_fields():
    for i in range (len (data_fields)):
        sys.stdout.write( u'%s\n' % data_fields[i])

def get_version():
    sys.stdout.write( u'%s, %s, %s, %s\n' % (name, version, author, email))

def get_dir(directory):
    dir = directory

def search_locations(location_str):
    base_url = 'http://xml.weather.co.ua/1.2/city/?search='
    xml_page = get_page(base_url + urllib.quote(location_str.encode('utf8')))
    tree = etree.XML(xml_page)
    xml_page = get_page('http://xml.weather.co.ua/1.2/country/')
    countries_tree = etree.XML(xml_page)
    #countries_tree = etree.parse('country.xml')
    cities = []
    ids = []
    countries = []
    #Для устранения проблемы отображенения символов кириллицы в MythWeather,
    #однако название страны по прежнему на русском, а следовательно - закорюками.
    #для версии MythTV 0.24 проблем с отображением кириллических символов нет, поэтому возвращаем русские названия городов
    #city_nodes = tree.xpath('//name_en') 
    city_nodes = tree.xpath('//name') 
    for node in city_nodes: 
        cities.append(node .text)
    id_nodes = tree.xpath('/city/city') 
    for node in id_nodes : 
        ids.append(node.values()[0])
    country_nodes = tree.xpath('//country_id') 
    for node in country_nodes : 
        countries.append(node.text)
    for i in range(len(city_nodes)):
        #Для устранения проблемы закорюк выковыриваем и английское название страны
        #country_ids = countries_tree.xpath('/country/country[@id=' + countries[i] + ']/name_en')
        country_ids = countries_tree.xpath('/country/country[@id=' + countries[i] + ']/name')
        sys.stdout.write(u'%s::%s, %s\n' % (ids[i], cities[i],  country_ids[0].text))

def get_data(location_id):
    
    def get_text_list(query):
        ret_list = []
        nodes = tree.xpath(query) 
        for node in nodes: 
            ret_list.append(node .text)
        return ret_list
    
    def get_icon(ico):
        if icons[ico] != '':
            return icons[ico]
        else:
            return 'unknown.png'

#Из значения облачности получаем тип погоды, тип погоды меняется каждый десяток
    def get_weather(WID):
        '''result = 255
        for i in range(0, 100, 10):
            max_value = i + 10
            if WID in range(i,  max_value):
                result = max_value'''
        result = WID/10
        return result
            
    def get_wind(WID):
        result = 255
        if WID<=20:
            result = 20
        elif WID<=35:
            result = 35
        elif WID<=55:
            result = 55
        elif WID<=70:
            result = 70
        elif WID<=110:
            result = 110
        elif WID<=125:
            result = 125
        elif WID<=145:
            result = 145
        elif WID<=160:
            result = 160
        elif WID<=200:
            result = 200
        elif WID<=215:
            result = 215
        elif WID<=235:
            result = 235
        elif WID<=250:
            result = 250
        elif WID<=290:
            result = 290
        elif WID<=305:
            result = 305
        elif WID<=325:
            result = 325
        elif WID<=340:
            result = 340
        elif WID<=360:
            result = 360
        return result

    base_url = 'http://xml.weather.co.ua/1.2/forecast/'
    xml_page = get_page(base_url + urllib.quote(location_id.encode('utf8')) + '?dayf=3&userid=YourSite_com&lang=ru')
    tree = etree.XML(xml_page)
    #tree = etree.parse(StringIO(xml_page))
   
    names = get_text_list('/forecast/city/name')
    #names = get_text_list('/forecast/city/name_en')
    picts = get_text_list('/forecast/current/pict')
    times = get_text_list('/forecast/current/time')
    clouds = get_text_list('/forecast/current/cloud')
    temps = get_text_list('/forecast/current/t')
    temp_fs = get_text_list('/forecast/current/t_flik')
    pressures = get_text_list('/forecast/current/p')
    winds = get_text_list('/forecast/current/w')
    wind_rumbs = get_text_list('/forecast/current/w_rumb')
    humidities = get_text_list('/forecast/current/h')


    for i in range(len(clouds)):
        sys.stdout.write( u'copyright::(c) DiscoveringWeather\n')
        sys.stdout.write( u'station_id::%s\n' % location_id)
        sys.stdout.write( u'cclocation:: %s\n' % names[0])
        sys.stdout.write( u'weather::%s\n' % unicode(weather[get_weather(int(clouds[0]))], 'utf8'))
        sys.stdout.write( u'weather_icon::%s\n' % get_icon(picts[0]))
        sys.stdout.write( u'temp::%s\n' % temps[0])
        sys.stdout.write( u'appt::%s\n' % temp_fs[0])
        sys.stdout.write( u'wind_dir::%s\n' % unicode(wind_dir[get_wind(int(wind_rumbs[0]))], 'utf8'))
        wind = float(winds[0])*3.6
        sys.stdout.write( u'wind_spdgst::%.1f\n' % wind)
        pressure = float(pressures[0])*001.33322368
        sys.stdout.write( u'pressure::%.1f\n' % pressure)
        sys.stdout.write( u'relative_humidity::%s\n' % humidities[0])
        sys.stdout.write( u'observation_time::%s\n' % times[0])

def main():
    parser = OptionParser(usage="""\
Usage: %prog [-l CITY | -u SI -d DIRECTORY LOCATIONID]
""")
    parser.add_option(  "-v", "--version", action="store_true", default=False, dest="version",
            help=u"Display version and author")
    parser.add_option("-d",  type="string", default=False, dest="dir_get",
            help="Return available data fields")
    parser.add_option("-t",  action="store_true", default=False, dest="fields_get",
            help="Return available data fields")
    parser.add_option("-T",  action="store_true", default=False, dest="timeouts_get", 
            help="Return timeouts")
    parser.add_option("-u", type="string", nargs = 4,  dest="data_get",
            metavar="LANGUAGE", default=False, 
            help="Get weather for city")
    parser.add_option(  "-l",  metavar="LANGUAGE", default=False, dest="locations_search",
            help=u"Type city for search")
    (options, args) = parser.parse_args()
    # Process version command line requests
    if options.version:
        get_version()
        sys.exit(0)
    if options.fields_get:
        get_fields()
        sys.exit(0)
    if options.timeouts_get:
        get_timeouts()
        sys.exit(0)
    if options.data_get:
        #get_data(unicode(options.data_get, "utf8"))
        get_data(options.data_get[3])
    elif options.locations_search:
        search_locations(unicode(options.locations_search, "utf8"))
        #search_locations(options.locations_search)
    elif options.dir_get:
        get_dir(unicode(options.dir_get, "utf8"))
    else:
        parser.print_usage()
        sys.exit(1)
    sys.exit(0)
    
if __name__ == '__main__':
	try:
		codecinfo = codecs.lookup('utf8')
		u2utf8 = codecinfo.streamwriter(sys.stdout)
		sys.stdout = u2utf8
		main()
	except SystemExit:
		pass
	except:
		print_exception(traceback.format_exc())
