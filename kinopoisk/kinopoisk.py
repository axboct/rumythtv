#!/usr/bin/python
# -*- coding: utf-8 -*-
#Часть кода не касающая собственно парсинга html основана на коде ofdb.py авторства Christian Güdel
#Автор Васильев Александр

import httplib,urllib,re
import urllib2
from lxml import html
from lxml import etree
import string
import time
import os
import sys
import traceback
import codecs
from optparse import OptionParser

kinopoisk_version = "0.1.1"
mythtv_version = "0.25"
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


def title_correction(title):
    try:
        regexp= re.compile(r'<.*?>')
        title = regexp.sub('',  title)
        return title
    except:
        return title
        

#Замена различных спецсимволов и тегов HTML на обычные символы, 
#возможно есть более правильное решение, но вроде и это работает.
def  normilize_string(processingstring):
    try:
        symbols_to_remove = {'&#160;':' ', '&nbsp;':' ', '&#161;':'¡', '&iexcl;':'¡', '&#162;':'¢', '&cent;':'¢', '&#163;':'£',  
        '&pound;':'£', '&#164;':'¤', '&curren;':'¤', '&#165;':'¥', '&yen;':'¥', '&#166;':'¦', '&brvbar;':'¦', '&brkbar;':',',
        '&#167;':'§', '&sect;':'§', '&#168;':'¨', '&uml;':'¨',  '&#169;':'©', '&copy;':'©', '&#170;':'ª', '&ordf;':'ª',  '&#171;':'«', 
        '&laquo;':'«', '&#172;':'¬', '&not;':'¬', '&#173;':' ', '&shy;':'­ ', '&#174;':'®', '&reg;':'®',
        '&#175;':'¯', '&macr;':'¯',  '&#176;':'°', '&deg;':'°', '&#177;':'±', '&plusmn;':'±', '&#178;':'²', '&sup2;':'²', 
        '&#179;':'³', '&sup3;':'³', '&#180;':'´', '&acute;':'´', '&#181;':'µ', '&micro;':'µ', '&#182;':'¶', '&para;':'¶', 
        '&#183;':'·', '&middot;':'·', '&#184;':'¸', '&cedil;':'¸', '&#185;':'¹', '&sup1;':'¹', '&#186;':'º', '&ordm;':'º', 
        '&#187;':'»', '&raquo;':'»', '&#188;':'¼', '&frac14;':'¼', '&#189;':'½', '&frac12;':'½', '&#190;':'¾', '&frac34;':'¾',
        '&#191;':'¿', '&iquest;':'¿', '&#192;':'À', '&Agrave;':'À', '&#193;':'Á', '&Aacute;':'Á', '&#194;':'Â', '&Acirc;':'Â', 
        '&#195;':'Ã', '&Atilde;':'Ã', '&#196;':'Ä', '&Auml;':'Ä', '&#197;':'Å', '&Aring;':'Å', '&#198;':'Æ', '&AElig;':'Æ', 
        '&#199;':'Ç', '&Ccedil;':'Ç', '&#200;':'È', '&Egrave;':'È', '&#201;':'É', '&Eacute;':'É', '&#202;':'Ê', '&Ecirc;':'Ê', 
        '&#203;':'Ë', '&Euml;':'Ë', '&#204;':'Ì', '&Igrave;':'Ì', '&#205;':'Í', '&Iacute;':'Í', '&#206;':'Î', '&Icirc;':'Î', 
        '&#207;':'Ï', '&Iuml;':'Ï', '&#208;':'Ð', '&ETH;':'Ð',  '&#209;':'Ñ', '&Ntilde;':'Ñ', '&#210;':'Ò', '&Ograve;':'Ò', 
        '&#211;':'Ó', '&Oacute;':'Ó', '&#212;':'Ô', '&Ocirc;':'Ô', '&#213;':'Õ', '&Otilde;':'Õ', '&#214;':'Ö', '&Ouml;':'Ö',
        '&#215;':'×', '&times;':'×', '&#216;':'Ø', '&Oslash;':'Ø', '&#217;':'Ù', '&Ugrave;':'Ù', '&#218;':'Ú', '&Uacute;':'Ú', 
        '&#219;':'Û', '&Ucirc;':'Û', '&#220;':'Ü', '&Uuml;':'Ü', '&#221;':'Ý', '&Yacute;':'Ý', '&#222;':'Þ', '&THORN;':'Þ', 
        '&#223;':'ß', '&szlig;':'ß', '&#224;':'à', '&agrave;':'à', '&#225;':'á', '&aacute;':'á', '&#226;':'â', '&acirc;':'â', 
        '&#227;':'ã', '&atilde;':'ã', '&#228;':'ä', '&auml;':'ä', '&#229;':'å', '&aring;':'å', '&#230;':'æ', '&aelig;':'æ', 
        '&#231;':'ç', '&ccedil;':'ç', '&#232;':'è', '&egrave;':'è', '&#233;':'é', '&eacute;':'é', '&#234;':'ê', '&ecirc;':'ê', 
        '&#235;':'ë', '&euml;':'ë', '&#236;':'ì', '&igrave;':'ì', '&#237;':'í', '&iacute;':'í', '&#238;':'î', '&icirc;':'î', 
        '&#239;':'ï', '&iuml;':'ï', '&#240;':'ð', '&eth;':'ð', '&#241;':'ñ', '&ntilde;':'ñ', '&#242;':'ò', '&ograve;':'ò', 
        '&#243;':'ó', '&oacute;':'ó', '&#244;':'ô', '&ocirc;':'ô', '&#245;':'õ', '&otilde;':'õ', '&#246;':'ö', '&ouml;':'ö', 
        '&#247;':'÷', '&divide;':'÷', '&#248;':'ø', '&oslash;':'ø', '&#249;':'ù', '&ugrave;':'ù', '&#250;':'ú', '&uacute;':'ú', 
        '&#251;':'û', '&ucirc;':'û', '&#252;':'ü', '&uuml;':'ü', '&#253;':'ý', '&yacute;':'ý', '&#254;':'þ', '&thorn;':'þ', 
        '&#255;':'ÿ', '&yuml;':'ÿ', '&#133;': '...', '&#151;':'-', '<br><br>':' ', '<br />':'',  '\r':'',  '\n':'', '  ':' '}
        for i in range (len(symbols_to_remove)):
            processingstring = string.replace(processingstring,  unicode(symbols_to_remove.items()[i][0],  'utf-8'), unicode(symbols_to_remove.items()[i][1],  'utf-8'))
        return processingstring
    except:
        return ''

def outXML(rootElm):
    outfile = sys.stdout
    handle = unicode(etree.tostring(rootElm, pretty_print=True, encoding='utf-8', xml_declaration=True), 'utf-8')
    outfile.writelines(handle)
    outfile.close()

#Получение HTML страницы
def get_page(address,  data=0,  title=''):
    try:
        opener = urllib2.build_opener()
        
        if data == 0:
            address = u'http://s.kinopoisk.ru' + address+urllib.quote(title.encode('utf8'))
        else:
            address = u'http://www.kinopoisk.ru' + address+urllib.quote(title.encode('utf8'))
        
        opener.addheaders = [("Host",  "www.kinopoisk.ru"), 
                                ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.0.14) Gecko/2009090216 Ubuntu/9.04 	(jaunty) Firefox/3.0.14'), 
                                ("Accept",  "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"), 
                                ("Accept-Language",  "ru,en-us;q=0.7,en;q=0.3"),
                                ("Accept-Charset",  "windows-1251,utf-8;q=0.7,*;q=0.7"),
                                ("Keep-Alive",  "300"),
                                ("Connection",  "keep-alive")]
        time.sleep(1)
        f = opener.open(address)
        return f.read().decode('cp1251')
    
    except:
        print_exception(traceback.format_exc())

#Ищем обои
def search_fanart(uid):
    try:
        data = get_page("/level/12/film/"+uid, 1)
        doc = html.document_fromstring(data)
        result = []
        
        posterNodes = doc.xpath("//div/table[@class='fotos fotos2']/tr/*") 
        for poster in posterNodes:
            hrefTag = poster.xpath("a")
            if len(hrefTag):
                posterURL= hrefTag[0].attrib["href"]
                result.append("http://www.kinopoisk.ru" + posterURL)
        return result

    except:
        print_exception(traceback.format_exc())

#Ищем обложки
def search_poster(uid):
    try:
        data = get_page("/level/17/film/"+uid, 1)
        doc = html.document_fromstring(data)
        result = []
        
        posterNodes = doc.xpath("//div/table[@class='fotos']/tr/*") 
        for poster in posterNodes:

            hrefTag = poster.xpath("a")
            if len(hrefTag):
                posterURL= hrefTag[0].attrib["href"]
                result.append("http://www.kinopoisk.ru" + posterURL)
            
        return result

    except:
        print_exception(traceback.format_exc())
        
#Получаем названия фильмов похожие на наш фильм
def search_title(title):

    data = get_page("/index.php?first=no&kp_query=",  0, title)
    doc = html.document_fromstring(data)
    
    #Проверяем ту ли страницу (т.е. страницу с результатами поиска) мы получили
    regexp= re.compile(unicode("Скорее всего, вы ищете", "utf8"), re.DOTALL)
    result = regexp.search(data)
    if result == None:
        #Если не ту, то парсим страницу фильма на которую нас перенаправил кинопоиск
        titlestr = doc.xpath("//h1[@class='moviename-big']") [0].text.strip()
        idstr = doc.xpath("//link[@rel='canonical']") [0].attrib["href"].split("/")[-2]
        sys.stdout.write( u'%s:%s\n' % (idstr, normilize_string(titlestr)))
    else:
        titleNodes = doc.xpath("//div[@class='search_results' or @class='search_results search_results_last']/div[@class='element most_wanted' or @class='element']/div[@class='info']") 
        
        for titleNode in titleNodes:
            titleInfo = titleNode.xpath("p[@class='name']/a")
            sys.stdout.write( u'%s:%s\n' % (titleInfo[0].attrib["href"].split("/")[-4], normilize_string(titleInfo[0].text)))

#Ищем и отдаем метаданные фильма
def search_data(uid, rating_country):

    #def addMultiValues(parentNode, parentNodeName, dataNode, xpathTuple, nodeName, valueName,  attributesDict={}):
    def addMultiValues(dataNode, xpathTuple):
        result = ''
        temp_list = []
        for xpathString in xpathTuple:
            if len(dataNode) and len(dataNode.xpath(xpathString)):
                for node in dataNode.xpath(xpathString):
                    if node.text != "...":
                        temp_list.append(node.text)
        result = ",".join(temp_list)
        return result

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
                #'writers' : '',
            }
        
        data = get_page("/level/1/film/"+uid, 1)
        doc = html.document_fromstring(data)
        
        filmdata['title'] = doc.xpath("//h1[@class='moviename-big']") [0].text.strip()
        
        userRatingNodes = doc.xpath("//div[@id='block_rating']/div/div/a/span")
        if len(userRatingNodes):
            filmdata['user_rating'] = userRatingNodes[0].text

        infoNodes = doc.xpath("//table[@class='info']/*") 
        for infoNode in infoNodes:
            dataNodes =infoNode.xpath("td")  
            if dataNodes[0].text == u"год":
                filmdata['year'] = dataNodes[1].xpath("div/a") [0].text
            elif dataNodes[0].text == u"страна":
                filmdata['countries'] = addMultiValues(dataNodes[1],  ("a", "div/a"))
            elif dataNodes[0].text == u"режиссер":
                filmdata['directors'] = addMultiValues(dataNodes[1], ("a", "div/a"))
            elif dataNodes[0].text == u"жанр":
                filmdata['genre'] = addMultiValues(dataNodes[1], ("a", "div/a"))
            elif dataNodes[0].text == u"время":
                filmdata['runtime']  = dataNodes[1].text.split()[0]
            elif dataNodes[0].text == u"рейтинг MPAA":
                filmdata['movie_rating'] = dataNodes[1].xpath("a")[0].attrib["href"].split("/")[-2]
        
        actorNodes = doc.xpath("//td[@class='actor_list']/div")
        if len(actorNodes):
            filmdata['cast'] = addMultiValues(actorNodes[0], ("a", "span/a"))

        descNodes = doc.xpath("//div[@class='brand_words']")
        filmdata['plot'] = normilize_string(descNodes[0].text)
        
        posters = search_poster(uid)
        if len(posters):
            filmdata['coverart'] = posters[0]
        
        fanarts = search_fanart(uid)
        if len(fanarts):
            filmdata['fanart'] = fanarts[0]

        filmdata['url'] = "http://www.kinopoisk.ru/level/1/film/"+uid

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
        getVersionInfo()
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
