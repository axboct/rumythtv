#!/usr/bin/python
# -*- coding: utf-8 -*-
#Часть кода не касающая собственно парсинга html основана на коде ofdb.py авторства Christian Güdel
#Автор Васильев Александр

import httplib,urllib,re
import urllib2
import string
import time
import os
import sys
import traceback
import codecs
from optparse import OptionParser

kinopoisk_version = "0.1"
mythtv_version = "0.23"
title = "The kinopoisk.ru Query"
author = "Alex Vasilyev"
usage_examples = ""

def comment_out(str):
	s = str
	try:
		s = unicode(str, "utf8")
	except:
		pass

	print("# %s" % (s,))

def debug_out(str):
	if VERBOSE:
		comment_out(str)

def response_out(str):
	if DUMP_RESPONSE:
		s = str
		try:
			s = unicode(str, "utf8")
		except:
			pass
		print(s)

def print_exception(str):
	for line in str.splitlines():
		comment_out(line)

#Замена различных спецсимволов и тегов HTML на обычные символы, 
#возможно есть более правильное решение, но вроде и это работает.
def  normilize_string(processingstring):
    try:
        symbol_to_remove=('&nbsp;', '&#151;', '<br><br>', '&laquo;', '&raquo;', '&#133;')
        symbol_to_remove2=(' ', '-', ' ',  '"',  '"',  '...', )
        for i in range (0,  len(symbol_to_remove)):
            processingstring = string.replace(processingstring, symbol_to_remove[i], symbol_to_remove2[i])
        return processingstring
    except:
        return ''

#Получение HTML страницы
def get_page(address,  title=''):
    headers = {"Host": "www.kinopoisk.ru",
        "User-Agent": "Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.0.14) Gecko/2009090216 Ubuntu/9.04 	(jaunty) Firefox/3.0.14",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en-us;q=0.7,en;q=0.3",
        "Accept-Charset": "windows-1251,utf-8;q=0.7,*;q=0.7",
        "Keep-Alive": "300",
        "Connection": "keep-alive"
        }
    data={}
    address = 'http://www.kinopoisk.ru' + address+urllib.quote(title.encode('utf8'))
    req = urllib2.Request(address, data,  headers)
    response = urllib2.urlopen(req)
    if response.code == 200:
        #С пятисекундной паузой у меня рабоатает лучше, не знаю кто виноват, 
        #сам кинопоиск или мой провайдер, вы можете попробовать закоментить следущую строку, чтобы исключить паузу.
        time.sleep(5)
        pagedata = response.read().decode('cp1251')
        return pagedata
    else:
        return None
        raise Exception( "get_page() error: ",response.code)   

def single_value(content,  matchstring):
    matchstring = unicode(matchstring, "utf8")
    regexp= re.compile(matchstring,re.DOTALL)
    result = regexp.search(content)
    if result != None:
        result = result.group(1)
        if result != None:
            return result
        else:
            return  ''
    else:
        return  ''
    
def multi_value(content,  matchstring, matchstring2):
    matchstring = unicode(matchstring , "utf8")
    matchstring2 = unicode(matchstring2 , "utf8")
    regexp= re.compile(matchstring,re.DOTALL)
    result = regexp.search(content)
    if  result != None:
        regexp = re.compile(matchstring2,re.DOTALL)
        result = regexp.finditer(result.group(0))
        if result != None:
            retList=[]
            for i in result:
                if i.group(1):
                    retList.append(i.group(1))
                else:
                    retList.append(i.group(0))
            result = retList
            return result
        else:
            return result
    else:
        return result

#Ищем обои
def search_fanart(uid):
    try:
        data = get_page("/level/12/film/"+uid)
        coveritems = []
        coveritems = multi_value(data,  '<table class="fotos.*?">(.*?)</table>', '<a href="(.*?)">')
        if coveritems != None:
            Coverart = coveritems[0]
            data = get_page(Coverart+uid)
            if  data != None:
                coveritem = single_value(data, '/picture/.*?src=\'(.*?)\' width=')
                return coveritem
            else:
                return ''
        else:
                return '' 
    except:
        print ''

#Ищем обложки
def search_poster(uid):
    try:
        data = get_page("/level/17/film/"+uid)
        coveritems = []
        coveritems = multi_value(data,  '<table class="fotos.*?">(.*?)</table>', '<a href="(.*?)">')
        if coveritems != None:
            data = get_page(coveritems[0]+uid)
            if  data != None:
                coveritem = single_value(data, '<a href="/picture/.*?src=\'(.*?)\' width=')
                #Выполняем дополнительный поиск, т.к. странички кинопоиск выдает всякие разные, 
                #возможно  еще какие-то варианты не учтены
                if coveritem == '':
                    coveritem = single_value(data, '<img alt=".*?src=\'(.*?)\' width=')
                    return coveritem
                else:
                    return coveritem
            else:
                return ''
        else:
            return ''
    except:
        print ''
        
#Получаем названия фильмов похожие на наш фильм
def search_title(title):
    def  get_item(content,  matchstring):
        matchstring = unicode(matchstring, "utf8")
        regexp  = re.compile(matchstring,re.DOTALL)
        ids = regexp.finditer(content.group(0))
        retList=[]
        for i in ids:
            if i.group(1):
                retList.append(i.group(1))
            else:
                retList.append(i.group(0))
        return retList
        
    data = get_page("/index.php?first=no&kp_query=",  title)
    #Проверяем ту ли страницу (т.е. страницу с результатами поиска) мы получили
    matchstring = 'Похожие результаты'
    matchstring = unicode(matchstring, "utf8")
    regexp= re.compile(matchstring,re.DOTALL)
    result = regexp.search(data)
    if result == None:
        #Если не ту, то парсим страницу фильма на которую нас перенаправил кинопоиск
        idstr = single_value(data, 'id_film = (.*?); <') 
        titlestr = single_value(data, 'class="moviename-big">(.*?)</h1>') 
        print normilize_string(idstr + ':' + titlestr)+'\n'
    else:
        #Если ту, то берем фильмы которые нам нашли
        matchstring = '>Скорее всего вы ищете:<(.*?)Если вам не удалось найти'
        matchstring = unicode(matchstring, "utf8")
        regexp= re.compile(matchstring,re.DOTALL)
        result = regexp.search(data)
        iditems = get_item(result ,  'href="/level/1/film/(.*?)/sr/1/"')
        titleitems = get_item(result ,  'href="/level/1/film/.*?sr/1/">(.*?)</a>')
        yearitems = get_item(result ,  'level/10/m_act.*?>(.*?)</a>')
        for i in range(0,  len(titleitems)):
                sys.stdout.write( u'%s:%s\n' % (iditems[i], normilize_string(titleitems[i]) + ' ('+ yearitems[i] + ')'))

#Ищем и отдаем метаданные фильма
def search_data(uid, rating_country):
    def get_multi_value(matchstring1, matchstring2):
        try:
            multi_valueList = multi_value(data,  matchstring1, matchstring2)
            if  multi_valueList != None:
                result = ",".join(multi_valueList)
                return result
            else:
                return ''
        except:
            return ''
    
    try:
        filmdata = {'title' : '',
                'countries' : '',
                'year' : '',
                'directors' : '',
                'cast' : '',
                'genre' : '',
                'user_rating' : '',
				'movie_rating' : '',
				'plot' : '',
#				'release_date' : '',
                'runtime' : '',
                'url' : '', 
                'coverart' : '',
                'fanart' : ''
                #				'writers' : '',
				}
        data = get_page("/level/1/film/"+uid)
        filmdata['title'] =normilize_string(single_value(data, 'class="moviename-big">(.*?)</h1>') )
        filmdata['directors'] = normilize_string(get_multi_value('td class="type">режиссер</td>(.*?)</tr>', '<a href=".*?>(.*?)</a>'))
        filmdata['countries'] = get_multi_value('<td class="type">страна</td>(.*?)</tr>', '<a href=".*?>(.*?)</a>')
        filmdata['year'] = single_value(data, 'td class="type">год</td>.*?<a href=.*?>(.*?)</a>')
        filmdata['genre'] = get_multi_value('td class="type">жанр</td>(.*?)</tr>', '<a href=".*?>(.*?)</a>')
        filmdata['user_rating'] = single_value(data, '<a href="/level/83/film/.*?>(.*?)<span')
        filmdata['plot'] = normilize_string(single_value(data, '<tr><td colspan=3 style="padding: 10px.*?reachbanner_">(.*?)</span>'))
        runtime = string.split(single_value(data, '<td class="time" id="runtime">(.*?)</td>'))
        filmdata['runtime'] = runtime[0]
        filmdata['cast'] = get_multi_value('<!-- актеры фильма -->(.*?)<!-- /актеры фильма -->',  'href="/level/4/people.*?class="all">(.*?)</a>')
        movierating = string.split(single_value(data, 'td class="type">рейтинг MPAA</td>.*?<img src.*?alt=(.*?) border=0>'))
        #Проверка нужна так как российские фильмы обычно не имеют рейтинга MPAA
        if len(movierating) > 0:
            filmdata['movie_rating'] = movierating[1]
        else:
            filmdata['movie_rating']=''
        filmdata['coverart'] = search_poster(uid)
        filmdata['fanart'] = search_fanart(uid)
        filmdata['url'] = "http://www.kinopoisk.ru/level/1/film/"+uid

#ReleaseDate:%(release_date)s
#Writers:%(writers)s
        print("""\
Title:%(title)s
Year:%(year)s
Director:%(directors)s
Plot:%(plot)s
UserRating:%(user_rating)s
Cast:%(cast)s
Genres:%(genre)s
Countries:%(countries)s
Runtime:%(runtime)s
MovieRating:%(movie_rating)s
Coverart:%(coverart)s
Fanart:%(fanart)s
URL:%(url)s
""" % filmdata)

    except:
        print_exception(traceback.format_exc())

def main():
    parser = OptionParser(usage="""\
Usage: %prog [-M TITLE | -D UID [-R COUNTRY[,COUNTRY]] | -P UID | -B UID]
""")
    parser.add_option(  "-u", "--usage", action="store_true", default=False, dest="usage",
                        help=u"Display examples for executing the tmdb script")
    parser.add_option(  "-v", "--version", action="store_true", default=False, dest="version",
                        help=u"Display version and author")
    parser.add_option("-M", "--title", type="string", dest="title_search",
            metavar="TITLE", help="Search for TITLE")
    parser.add_option("-D", "--data", type="string", dest="data_search",
            metavar="UID", help="Search for video data for UID")
    parser.add_option("-R", "--rating-country", type="string",
            dest="ratings_from", metavar="COUNTRY",
            help="When retrieving data, use ratings from COUNTRY")
    parser.add_option("-P", "--poster", type="string", dest="poster_search",
            metavar="UID", help="Search for images associated with UID")
    parser.add_option("-B", "--fanart", type="string", dest="fanart_search",
            metavar="UID", help="Search for images associated with UID")
    parser.add_option("-d", "--debug", action="store_true", dest="verbose",
            default=False, help="Display debug information")
    parser.add_option("-r", "--dump-response", action="store_true",
            dest="dump_response", default=False,
            help="Output the raw response")
    parser.add_option(  "-l", "--language", metavar="LANGUAGE", default=u'ru', dest="language",
            help=u"Select data that matches the specified language fall back to english if nothing found (e.g. 'ru' Russian' es' Español, 'de' Deutsch ... etc)")
    
    (options, args) = parser.parse_args()

    global VERBOSE, DUMP_RESPONSE
    VERBOSE = options.verbose
    DUMP_RESPONSE = options.dump_response
    # Process version command line requests
    if options.version:
        sys.stdout.write("%s (%s) by %s\n" % (
        title, kinopoisk_version, author))
        sys.exit(0)
    # Process usage command line requests
    if options.usage:
        sys.stdout.write(usage_examples)
        sys.exit(0)
    if options.title_search:
        search_title(unicode(options.title_search, "utf8"))
        #search_title(options.title_search)
    elif options.data_search:
        rf = options.ratings_from
        if rf:
            rf = unicode(rf, "utf8")
        #search_data(unicode(options.data_search, "utf8"), rf)
        search_data(options.data_search, rf)
    elif options.poster_search:
        search_poster(unicode(options.poster_search, "utf8"))
        #search_poster(options.poster_search)
    elif options.fanart_search:
        search_fanart(unicode(options.fanart_search, "utf8"))
        #search_fanart(options.fanart_search)
    else:
        parser.print_usage()
        sys.exit(1)

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

# vim: ts=4 sw=4:
