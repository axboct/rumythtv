#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script is partially based on script dwua_xml.pl by Victor Bron 
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
try: set
except NameError: from sets import Set as set

name = 'WCU-3D-XML';
version = 0.01;
author = 'Alex Vasilyev';
email = 'sandybigboy@gmail.ru';

update_timeout = 120*60
retrieve_timeout = 30

data_fields = ('3dlocation', '6dlocation',  'updatetime', 
        'high-0', 'high-1', 'high-2', 'high-3', 'high-4', 'high-5',
        'low-0', 'low-1', 'low-2', 'low-3', 'low-4', 'low-5',
        'icon-0', 'icon-1', 'icon-2', 'icon-3', 'icon-4', 'icon-5',
        'date-0', 'date-1', 'date-2', 'date-3', 'date-4', 'date-5')

icons = {'_0_moon.gif' : 'sunny.png',  '_0_sun.gif' :  'sunny.png',  '_1_moon_cl.gif' :  'pcloudy.png', 
            '_1_sun_cl.gif' : 'pcloudy.png',  '_2_cloudy.gif' : 'mcloudy.png', '_3_pasmurno.gif' :  'cloudy.png', 
            '_4_short_rain.gif' : 'lshowers.png', '_5_rain.gif' : 'showers.png',  '_6_lightning.gif' : 'thunshowers.png', 
            '_7_hail.gif' :  'fog.png',  'ico=~/^_8_rain_snow.gif' :  'rainsnow.png', 'ico=~ /_9_snow.gif' : 'snowshow.png',  
            '_10_heavy_snow.gif' :  'snowshow.png','_255_NA.gif' : 'unknown.png'
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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.0.14) Gecko/2009090216 Ubuntu/9.04 	(jaunty) Firefox/3.0.14",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en-us;q=0.7,en;q=0.3",
        "Accept-Charset": "windows-1251,utf-8;q=0.7,*;q=0.7",
        "Keep-Alive": "300",
        "Connection": "keep-alive"
        }
    data={}
    req = urllib2.Request(address, data,  headers)
    response = urllib2.urlopen(req)
    if response.code == 200:
        pagedata = response.read()
        return pagedata
    else:
        return None
        raise Exception( "get_page() error: ",response.code)   

def uniquer(seq, f=None):
    if f is None:
        def f(x): return x
    already_seen = set( )
    result = [  ]
    for item in seq:
        marker = f(item)
        if marker not in already_seen:
             already_seen.add(marker)
             result.append(item)
    return result

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
    
    cities = []
    ids = []
    countries = []
    
    city_nodes = tree.xpath('//name_en') 
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
        country_ids = countries_tree.xpath('/country/country[@id=' + countries[i] + ']/name_en')
        sys.stdout.write( u'%s::%s, %s\n' % (ids[i], cities[i],  country_ids[0].text))

def get_data(location_id):
    
    def get_text_list(query):
        ret_list = []
        nodes = tree.xpath(query) 
        for node in nodes: 
            ret_list.append(node .text)
        return ret_list
    
    def get_value_list(query):
        ret_list = []
        nodes = tree.xpath(query) 
        for node in nodes: 
            ret_list.append(node .values()[0])
        return ret_list

    def get_icon(ico):
        if icons[ico] != '':
            return icons[ico]
        else:
            return 'unknown.png'

    #Из значения облачности получаем тип погоды, тип погоды меняется каждый десяток
    def get_weather(WID):
        result = 255
        for i in range(0, 90, 10):
            max_value = i + 10
            if WID in range(i,  max_value):
                result = max_value
        return result

    def get_data(days):
        t_mins = []
        t_maxs = []
        picts = []
        forecast_for_date = tree.xpath('/forecast/forecast/day[@date=' + '"'+days[i] + '"'+ ']/*') 
        datesplitted = days[i].split('-')
        when = datetime.datetime(int(datesplitted[0]),  int(datesplitted[1]),  int(datesplitted[2]))
        for nodes in forecast_for_date:
            if len(nodes) < 2:
                if nodes.tag == 'pict':
                    picts.append(nodes.text)
            else:
                if nodes.tag == 't':
                    for node in nodes:
                        if node.tag == 'min':
                            t_mins.append(int(node.text))
                        elif node.tag == 'max':
                            t_maxs.append(int(node.text))
        pict_count = len(picts)
        #Выводим данные
        sys.stdout.write( u'date-%s::%s\n' % (str(i),  when.strftime('%w')))
        if pict_count > 3:
            sys.stdout.write( u'icon-%s::%s\n' % (str(i),  get_icon(picts[pict_count-2])))
        else:
            sys.stdout.write( u'icon-%s::%s\n' % (str(i),  get_icon(picts[pict_count-1])))
        sys.stdout.write( u'low-%s::%s\n' % (str(i),  min(t_mins)))
        sys.stdout.write( u'high-%s::%s\n' % (str(i),  max(t_maxs)))
    
    base_url = 'http://xml.weather.co.ua/1.2/forecast/'
    xml_page = get_page(base_url + urllib.quote(location_id.encode('utf8')) + '?dayf=5&userid=YourSite_com&lang=ru')
    tree = etree.XML(xml_page)
    #tree = etree.parse(StringIO(xml_page))
    names = get_text_list('/forecast/city/name_en')
    sys.stdout.write( u'3dlocation::%s\n' % names[0])
    sys.stdout.write( u'6dlocation::%s\n' % names[0])
    updatetimes = tree.xpath('/forecast[@version]')
    sys.stdout.write( u'updatetime::%s\n' % updatetimes[0].values()[1])
    days = get_value_list('/forecast/forecast/day[@date]')
    days = uniquer(days)
    for i in range(len(days)):
        if len(days) > 5:
            get_data(days)
        else:
            get_data(days)
            
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
            help=u"Введите название города")
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
        #get_data(unicode(options.data_get[3], "utf8"))
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
