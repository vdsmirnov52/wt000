#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import	psycopg2, psycopg2.extensions
import	time

#print "Content-Type: text/html; charset=utf-8\n"


LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"		# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)


def	main (SCRIPT_NAME, request, referer):
	print "~log|ajax.maim"
	try:
		print "~shadow|", request
		if request.has_key ('shstat'):
			shstat = request ['shstat']
			print	"~error|~warnn|", os.environ['SERVER_NAME']
			if shstat == 'clear':
				print "ZZZZ"
			else:
				print "~eval|alert ('Unknown shstat: [%s]!');" % request ['shstat']
		else:
			print "~shadow|"
			wdgerror ("Отсутствует request[shstat]",  txt = "request: %s" % str(request), obj = SS.objpkl)
		#	out_widget('warnn', tit = "Отсутствует request[shstat]",  txt = "request: %s" % str(request), obj = SS.objpkl)
		
	except psycopg2.OperationalError:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~eval|alert (\"EXCEPT: ajax Нет доступа к БД:\\n", ddb_map, "\");"
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~error|<span class='error'>EXCEPT:", exc_type, exc_value, "</span>"
	#	print "~eval|alert (\"EXCEPT: ajax.py shstat: ", shstat, "\\n", exc_type, exc_value, "\");"
